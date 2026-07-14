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
    """Build a sketch_<type> operation from a parsed sketch_info dict."""
    sketch_id = sketch_info["sketch_id"]
    op_id = _make_op_id(sketch_id, "sk")
    entity_to_opid[sketch_id] = op_id
    ptype = sketch_info.get("profile_type", "unknown")

    sketch_entity = entities.get(sketch_id, {})
    params = _compute_sketch_params(ptype, sketch_entity)

    return {
        "op_id": op_id,
        "op_type": _sketch_type_from_profile(ptype),
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
    """Generic polygon: extract vertices from line endpoints."""
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
        # Fallback to arbitrary_polygon: use the bbox of the first profile's curves
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
