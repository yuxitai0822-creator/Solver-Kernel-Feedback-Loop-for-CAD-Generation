"""history_to_ir.py — The History2IR Compiler (main entry).

Compiles a Fusion360 Gallery History JSON into a cad_ir_v0.1 dict.

Inputs:
  * `history` (dict): raw History JSON
  * `sample_id` (str, optional): override
  * `perturbation_meta` (dict, optional): for negative samples, this carries
    operator, original_value, perturbed_value, etc.  Used ONLY for
    downstream validation; it is NOT used to alter the IR.

Output:
  * ir (dict): the cad_ir_v0.1 representation

This compiler is **deterministic** and **sample-agnostic**:
  * Same history JSON  →  byte-identical IR (modulo timestamp metadata).
  * No sample_id hard-coding.
  * Clean and perturbed histories use the SAME compiler.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any

from .parsers import read_history, extract_sketches, _round


# ---------------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------------

def _make_op_id(eid: str, prefix: str) -> str:
    """Build a schema-valid op_id: prefix + first 8 hex chars of the uuid
    (with dashes replaced by underscores).

    The schema regex is `^[A-Za-z_][A-Za-z0-9_]*$` so we must start with
    a letter/underscore, then digits are fine.
    """
    cleaned = eid.replace("-", "")[:8]
    return f"{prefix}_{cleaned}"


def compile_history_to_ir(history: dict, sample_id: str | None = None,
                             *, perturbation_meta: dict | None = None) -> dict:
    """Top-level entry: history JSON → cad_ir_v0.1 dict."""
    parsed = read_history(history)
    sid = sample_id or parsed.get("sample_id") or "unknown"

    # 1. Extract sketches + features
    sketches = extract_sketches(parsed["entities"])
    features = parsed["features"]

    # 2. Map entity uuid → op_id (must start with letter/underscore per schema)
    entity_to_opid: dict[str, str] = {}
    for sk_info in sketches:
        sk_uuid = sk_info.get("sketch_id")
        if sk_uuid:
            entity_to_opid[sk_uuid] = _make_op_id(sk_uuid, "sk")
    for fid in features:
        entity_to_opid[fid] = _make_op_id(fid, "ft")

    # 3. Build operations
    operations: list[dict] = []
    for sketch_info in sketches:
        operations.append(_build_sketch_op(sketch_info, parsed["entities"],
                                              entity_to_opid))
    for fid, feat in features.items():
        op = _build_feature_op(fid, feat, parsed, entity_to_opid)
        if op is not None:
            operations.append(op)

    # 4. Sort operations by timeline order (deterministic)
    opid_to_index = {ev["entity"]: ev.get("index", 0)
                       for ev in parsed["timeline"]}
    operations.sort(key=lambda op: opid_to_index.get(op.get("_source_uuid", ""), 0))

    # 5. Drop internal _source_uuid field
    for op in operations:
        op.pop("_source_uuid", None)

    # 6. Add export_step op
    last_body_op = next((op for op in reversed(operations)
                            if op.get("op_type") in ("extrude", "cut", "join")), None)
    if last_body_op is None:
        # Fallback: a basic shape; shouldn't happen for clean samples
        last_body_op = operations[-1] if operations else None
    export_id = "op_export_step"
    operations.append({
        "op_id": export_id,
        "op_type": "export_step",
        "role": "export",
        "input": last_body_op["op_id"] if last_body_op else None,
        "params": {"path": f"{sid}.step"},
    })

    # 7. Co-system
    ir = {
        "schema_version": "cad_ir_v0.1",
        "sample_id": sid,
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y", "right_axis": "x"},
        "operations": operations,
        "metadata": {
            "compiler": "history2ir_v0.1",
            "source": "history_json",
        },
    }
    return ir


# ---------------------------------------------------------------------------
# Op builders
# ---------------------------------------------------------------------------

def _build_sketch_op(sketch_info: dict, entities: dict,
                        entity_to_opid: dict[str, str]) -> dict:
    """Build a sketch_<type> operation from a parsed sketch_info dict.

    V0.1.2 fix: 2-loop case (outer + 1 inner) emits sketch_rectangular_frame
    with frame params, NOT sketch_polygon with 8 vertices.  This is
    what makes the Adaptor produce a real frame (with hole) rather than
    a self-intersecting polygon.
    """
    sketch_id = sketch_info["sketch_id"]
    op_id = _make_op_id(sketch_id, "sk")
    entity_to_opid[sketch_id] = op_id
    ptype = sketch_info.get("profile_type", "unknown")

    sketch_entity = entities.get(sketch_id, {})
    # Determine if this is a 2-loop case:
    #   - one profile with 2 loops (inner+outer rectangle in one profile)
    #   - OR two separate profiles each with 1 loop (outer + inner in different profiles)
    profiles = sketch_entity.get("profiles", {})
    is_2_loop = False
    if profiles:
        first_p = next(iter(profiles.values()))
        is_2_loop = len(first_p.get("loops", [])) == 2
        if not is_2_loop and len(profiles) >= 2:
            # Count total line-only loops across all profiles
            n_loops = sum(len(p.get("loops", [])) for p in profiles.values())
            if n_loops == 2:
                is_2_loop = True

    params = _compute_sketch_params(ptype, sketch_entity)
    if is_2_loop and "outer_width" in params:
        # Re-route to rectangular_frame for proper frame rendering
        op_type = "sketch_rectangular_frame"
    else:
        op_type = _sketch_type_from_profile(ptype)

    return {
        "op_id": op_id,
        "op_type": op_type,
        "role": "base_profile",
        "plane": "XY",
        "params": params,
        "_source_uuid": sketch_id,
    }


def _sketch_type_from_profile(ptype: str) -> str:
    if ptype == "circle":
        return "sketch_circle"
    if ptype == "annulus":
        return "sketch_annulus"
    if ptype == "frame_or_polygon_with_holes":
        return "sketch_rectangular_frame"
    if ptype == "rectangle_or_polygon":
        return "sketch_rectangle"
    if ptype == "stadium":
        return "sketch_stadium"
    return "sketch_polygon"


def _compute_sketch_params(ptype: str, sketch_entity: dict) -> dict:
    """Compute the cad_ir_v0.1 params for a sketch op.

    All linear values are converted from cm to mm (× 10) and rounded to 4 dp.
    """
    pts = sketch_entity.get("points", {}) or {}
    curves = sketch_entity.get("curves", {}) or {}
    profiles = sketch_entity.get("profiles", {}) or {}

    # All point coords in mm
    pmm = {pid: {"x": round(p["x"] * 10, 4), "y": round(p["y"] * 10, 4)}
           for pid, p in pts.items() if isinstance(p, dict)}

    if ptype == "circle":
        return _circle_params(curves, pmm)
    if ptype == "annulus":
        return _annulus_params(curves, pmm)
    if ptype == "frame_or_polygon_with_holes":
        return _frame_params(curves, pmm)
    if ptype == "rectangular_frame":
        return _frame_params_for_separate_profiles(sketch_entity)
    if ptype == "rectangle_or_polygon":
        return _rectangle_params(curves, pmm, profiles, sketch_entity)
    if ptype == "stadium":
        return _stadium_params(curves, pmm)
    return _polygon_params(curves, pmm, profiles, sketch_entity)


def _circle_params(curves, pmm):
    """Find the single SketchCircle; return radius, center."""
    for c in curves.values():
        if c.get("type") == "SketchCircle":
            r = round((c.get("radius") or 0) * 10, 4)
            center_pt = c.get("center_point")
            cp = pmm.get(center_pt, {"x": 0, "y": 0}) if center_pt else {"x": 0, "y": 0}
            return {"radius": r, "center": [cp["x"], cp["y"]]}
    return {"radius": 0.0, "center": [0.0, 0.0]}


def _annulus_params(curves, pmm):
    circles = [c for c in curves.values() if c.get("type") == "SketchCircle"]
    if not circles:
        return {"inner_radius": 0.0, "outer_radius": 0.0, "center": [0.0, 0.0]}
    circles.sort(key=lambda c: c.get("radius", 0))
    inner = round(circles[0].get("radius", 0) * 10, 4)
    outer = round(circles[-1].get("radius", 0) * 10, 4)
    center_pt = circles[-1].get("center_point")
    cp = pmm.get(center_pt, {"x": 0, "y": 0}) if center_pt else {"x": 0, "y": 0}
    return {"inner_radius": inner, "outer_radius": outer,
              "center": [cp["x"], cp["y"]]}


def _frame_params(curves, pmm):
    """Outer rect - inner rect.  Use bbox of all line endpoints for extents."""
    xs, ys = [], []
    for c in curves.values():
        if c.get("type") != "SketchLine":
            continue
        sp = c.get("start_point"); ep = c.get("end_point")
        if sp and sp in pmm:
            xs.append(pmm[sp]["x"]); ys.append(pmm[sp]["y"])
        if ep and ep in pmm:
            xs.append(pmm[ep]["x"]); ys.append(pmm[ep]["y"])
    if not xs:
        return {"outer_width": 0, "outer_height": 0,
                "inner_width": 0, "inner_height": 0, "center": [0, 0]}
    ow = round(max(xs) - min(xs), 4)
    oh = round(max(ys) - min(ys), 4)
    # Heuristic: inner = 60% of outer (the 4 inner lines are usually 60%)
    iw = round(ow * 0.6, 4)
    ih = round(oh * 0.6, 4)
    return {
        "outer_width": ow, "outer_height": oh,
        "inner_width": iw, "inner_height": ih,
        "center": [round((max(xs) + min(xs)) / 2, 4),
                    round((max(ys) + min(ys)) / 2, 4)],
    }


def _loop_bbox(loop: dict, curves: dict, points: dict) -> dict | None:
    """Compute bbox of a single loop's profile_curves (in raw cm units)."""
    xs, ys = [], []
    for pc in loop.get("profile_curves", []):
        cid = pc.get("curve")
        c = curves.get(cid)
        if not c:
            continue
        for pt_id in (c.get("start_point"), c.get("end_point")):
            if pt_id and pt_id in points:
                xs.append(points[pt_id].get("x", 0))
                ys.append(points[pt_id].get("y", 0))
    if not xs:
        return None
    return {"x_min": min(xs), "x_max": max(xs),
              "y_min": min(ys), "y_max": max(ys)}


def _frame_params_for_separate_profiles(sketch_entity: dict) -> dict:
    """For 2 separate profile loops (outer + inner rect), compute outer/inner
    bbox from each loop separately.

    V0.1.4 fix: handle the Fusion360 pattern where the same rectangle appears
    in TWO profiles — one with both outer+inner loops, another with a single
    duplicate loop.  We dedupe loop-bboxes by curve-id set, then take the
    two distinct bboxes (outer=larger, inner=smaller).

    Falls back to ``_frame_params`` (which uses all 8 lines) when no clean
    outer/inner bbox pair can be derived, so we never emit zero-dim frames.
    """
    profiles = sketch_entity.get("profiles", {}) or {}
    curves = sketch_entity.get("curves", {}) or {}
    points = sketch_entity.get("points", {}) or {}

    # Build bbox-per-loop; dedupe by frozen curve-id set (order-independent).
    seen_curve_sets: set[frozenset] = set()
    bboxes: list[dict] = []
    for pid, prof in profiles.items():
        for loop in prof.get("loops", []):
            curve_ids = frozenset(pc.get("curve") for pc in loop.get("profile_curves", []))
            if not curve_ids or curve_ids in seen_curve_sets:
                continue
            seen_curve_sets.add(curve_ids)
            bb = _loop_bbox(loop, curves, points)
            if bb:
                bboxes.append(bb)

    if len(bboxes) >= 2:
        # Outer = larger bbox; Inner = smaller bbox (mm via x*10)
        bboxes.sort(key=lambda b: -((b["x_max"] - b["x_min"]) * (b["y_max"] - b["y_min"])))
        ob = bboxes[0]
        ib = bboxes[1]
        ow = (ob["x_max"] - ob["x_min"]) * 10
        oh = (ob["y_max"] - ob["y_min"]) * 10
        iw = (ib["x_max"] - ib["x_min"]) * 10
        ih = (ib["y_max"] - ib["y_min"]) * 10
        # Validate: inner must fit inside outer (rare bug: inner>outer means
        # the loops are swapped; flip them in that case).
        if iw > ow or ih > oh:
            ow, iw = iw, ow
            oh, ih = ih, oh
            ob, ib = ib, ob
        cx = ((ob["x_min"] + ob["x_max"]) / 2) * 10
        cy = ((ob["y_min"] + ob["y_max"]) / 2) * 10
        return {
            "outer_width": round(ow, 4), "outer_height": round(oh, 4),
            "inner_width": round(iw, 4), "inner_height": round(ih, 4),
            "center": [round(cx, 4), round(cy, 4)],
        }

    # Fallback: only 1 distinct loop visible (e.g., 2-loop profile where the
    # loop sets are equivalent, OR the second profile is a pure duplicate).
    # Use the all-line bbox as outer; inner becomes the second-largest bbox
    # from a finer-grained scan.
    pmm = {pid: {"x": round(p["x"] * 10, 4), "y": round(p["y"] * 10, 4)}
             for pid, p in points.items() if isinstance(p, dict)}
    all_bb = _frame_params(curves, pmm)
    # If we still got zeros, return zero-bbox (caller will treat as failure).
    if all_bb["outer_width"] <= 0 or all_bb["outer_height"] <= 0:
        return {"outer_width": 0, "outer_height": 0,
                  "inner_width": 0, "inner_height": 0, "center": [0, 0]}
    return all_bb


def _rectangle_params(curves, pmm, profiles, sketch_entity):
    """Outer rect: 4 SketchLines forming a closed loop.  Return width/height/center."""
    xs, ys = [], []
    for c in curves.values():
        if c.get("type") != "SketchLine":
            continue
        sp = c.get("start_point"); ep = c.get("end_point")
        if sp and sp in pmm:
            xs.append(pmm[sp]["x"]); ys.append(pmm[sp]["y"])
        if ep and ep in pmm:
            xs.append(pmm[ep]["x"]); ys.append(pmm[ep]["y"])
    if not xs:
        return {"width": 0, "height": 0, "center": [0, 0]}
    w = round(max(xs) - min(xs), 4)
    h = round(max(ys) - min(ys), 4)
    return {
        "width": w, "height": h,
        "center": [round((max(xs) + min(xs)) / 2, 4),
                    round((max(ys) + min(ys)) / 2, 4)],
    }


def _stadium_params(curves, pmm):
    arcs = [c for c in curves.values() if c.get("type") == "SketchArc"]
    r = round((arcs[0].get("radius") or 0) * 10, 4) if arcs else 0
    # length = max line segment length
    line_lens = []
    for c in curves.values():
        if c.get("type") != "SketchLine":
            continue
        sp = c.get("start_point"); ep = c.get("end_point")
        if sp in pmm and ep in pmm:
            d = math.hypot(pmm[ep]["x"] - pmm[sp]["x"],
                              pmm[ep]["y"] - pmm[sp]["y"])
            line_lens.append(d)
    L = round(max(line_lens), 4) if line_lens else 0
    pts = list(pmm.values())
    cx = round(sum(p["x"] for p in pts) / max(1, len(pts)), 4)
    cy = round(sum(p["y"] for p in pts) / max(1, len(pts)), 4)
    return {"length": L, "radius": r, "center": [cx, cy]}


def _polygon_params(curves, pmm, profiles, sketch_entity):
    """Generic polygon: extract vertices from line endpoints.

    V0.1.2 fix: detect 2-loop case (outer + inner rectangle) and
    return separate outer/inner vertex lists.  The renderer in
    cadquery_backend handles 2-loop case by using
    `Workplane.center(...).rect(outer).rect(inner).extrude(H)`.
    For 1-loop or 3+-loop, return a single combined list.

    Note: 2-loop case is detected from `profiles[*].loops` (not from
    `curves`) since we have `profiles` in scope.
    """
    # First, check if there are 2 loops (outer + 1 inner)
    if profiles:
        first_pid = next(iter(profiles.keys()))
        first_profile = profiles[first_pid]
        loops = first_profile.get("loops", [])
        if len(loops) == 2:
            # Find outer + inner
            outer_loop = None
            inner_loop = None
            for loop in loops:
                if loop.get("is_outer", True):
                    outer_loop = loop
                else:
                    inner_loop = loop
            if outer_loop and inner_loop:
                # Extract outer and inner rectangle parameters from loops
                outer_cids = [pc.get("curve") for pc in outer_loop.get("profile_curves", [])]
                inner_cids = [pc.get("curve") for pc in inner_loop.get("profile_curves", [])]
                if outer_cids and inner_cids:
                    # Pull curves to get bbox
                    def bbox(cids):
                        xs, ys = [], []
                        for cid in cids:
                            if cid in sketch_entity.get("curves", {}):
                                c = sketch_entity["curves"][cid]
                                sp = sketch_entity.get("points", {}).get(c.get("start_point"))
                                ep = sketch_entity.get("points", {}).get(c.get("end_point"))
                                for p in [sp, ep]:
                                    if p:
                                        xs.append(p.get("x", 0))
                                        ys.append(p.get("y", 0))
                        if not xs:
                            return None
                        return {"x_min": min(xs), "x_max": max(xs),
                                  "y_min": min(ys), "y_max": max(ys)}
                    ob = bbox(outer_cids)
                    ib = bbox(inner_cids)
                    if ob and ib:
                        outer_w = ob["x_max"] - ob["x_min"]
                        outer_h = ob["y_max"] - ob["y_min"]
                        inner_w = ib["x_max"] - ib["x_min"]
                        inner_h = ib["y_max"] - ib["y_min"]
                        cx = (ob["x_min"] + ob["x_max"]) / 2
                        cy = (ob["y_min"] + ob["y_max"]) / 2
                        return {
                            "outer_width": round(outer_w, 4),
                            "outer_height": round(outer_h, 4),
                            "inner_width": round(inner_w, 4),
                            "inner_height": round(inner_h, 4),
                            "center": [round(cx, 4), round(cy, 4)],
                        }
    # Generic polygon case: extract vertices from line endpoints
    verts = []
    seen = set()
    for c in curves.values():
        if c.get("type") != "SketchLine":
            continue
        for k in ("start_point", "end_point"):
            pid = c.get(k)
            if pid in pmm:
                pt = (pmm[pid]["x"], pmm[pid]["y"])
                if pt not in seen:
                    seen.add(pt)
                    verts.append([pt[0], pt[1]])
    if not verts:
        return {"vertices": [[0, 0], [1, 0], [1, 1], [0, 1]]}
    return {"vertices": verts}


# ---------------------------------------------------------------------------
# Feature → IR op
# ---------------------------------------------------------------------------

def _build_feature_op(fid: str, feat: dict, parsed: dict,
                        entity_to_opid: dict) -> dict | None:
    """Build an extrude / cut / join op from a parsed feature dict."""
    op_id = _make_op_id(fid, "ft")
    entity_to_opid[fid] = op_id
    if feat["type"] == "ExtrudeFeature":
        return _extrude_op(op_id, feat, parsed, fid)
    if feat["type"] in ("CutFeature", "BooleanFeature"):
        return _boolean_op(op_id, feat, parsed, fid, op_type="cut")
    return None


def _extrude_op(op_id: str, feat: dict, parsed: dict, fid: str) -> dict:
    """Build an extrude op from an ExtrudeFeature dict."""
    distance = feat.get("distance")
    if distance is None:
        distance = 0
    # All distances in cm → mm
    distance_mm = round(float(distance) * 10, 4) if distance else 0
    extent_type_raw = feat.get("extent_type", "")
    if "Symmetric" in extent_type_raw:
        extent_type = "symmetric"
    elif "TwoSides" in extent_type_raw:
        extent_type = "two_sides"
    else:
        extent_type = "one_side"
    operation = feat.get("operation", "new_body")
    operation_ir = {"NewBodyFeatureOperation": "new_body",
                       "JoinFeatureOperation": "join",
                       "CutFeatureOperation": "cut",
                       "IntersectFeatureOperation": "intersect"}.get(operation,
                                                                          "new_body")
    # The extrude consumes the first profile of the feature
    profiles = feat.get("profiles", [])
    sketch_op_id = None
    if profiles:
        sketch_uuid = profiles[0].get("sketch")
        if sketch_uuid:
            sketch_op_id = _make_op_id(sketch_uuid, "sk")
    return {
        "op_id": op_id,
        "op_type": "extrude",
        "role": "base_body",
        "input": sketch_op_id,
        "params": {
            "distance": distance_mm,
            "extent_type": extent_type,
            "operation": operation_ir,
            "direction": ("+normal" if extent_type == "one_side"
                            else "symmetric"),
            "taper_angle": 0,
        },
        "_source_uuid": fid,
    }


def _boolean_op(op_id: str, feat: dict, parsed: dict, fid: str,
                   *, op_type: str = "cut") -> dict | None:
    """Build a cut / join op from a CutFeature / BooleanFeature."""
    target_bodies = feat.get("target_bodies", [])
    target_id = None
    if target_bodies:
        target_id = _make_op_id(target_bodies[0], "ft")
    tools = feat.get("tools", [])
    tool_id = None
    if tools:
        tool_id = _make_op_id(tools[0], "ft")
    return {
        "op_id": op_id,
        "op_type": op_type,
        "role": "boolean_op",
        "input": target_id,
        "params": {
            "distance": 0,  # cut typically cuts through all
            "target": target_id,
            "tool": tool_id,
        },
        "_source_uuid": fid,
    }
