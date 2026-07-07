"""operators.py — E1-E6 perturbation operators.

Design rules
------------
* History JSON schema (Fusion360 Gallery reconstruction):
    entities[UUID] = Sketch  | ExtrudeFeature | ...
    Sketch:     points, curves, profiles[loops[profile_curves]]
                curves[i] = SketchLine | SketchCircle | SketchArc
    ExtrudeFeature: profiles[{profile, sketch}], extent_one.distance.value,
                     extent_type ("OneSideFeatureExtentType" | "SymmetricFeatureExtentType" | "TwoSidesFeatureExtentType")
* All operators are PURE functions: they take a parsed history dict and return
  (perturbed_history, perturbed_design_plan, perturbation_meta).
* Operations modify ONLY history points / curves / profiles / extrude.distance
  fields. They do not modify constraints or dimensions (which are not consumed
  by the reconstruction engine anyway).
* Scale factors are bounded so the perturbed CAD still has realistic geometry
  (no zero radius, no inner_radius >= outer_radius except for explicit validity
  negatives).

Output perturbation_meta
------------------------
    perturbation_type:  one of E1..E6
    error_category:     E1_envelope_dim | E2_extrude_depth | ...
    target_intent:      KQP intent primarily affected
    expected_failed_query: KQP query id(s) primarily affected (list)
    allowed_secondary_failed_queries: KQP intents that may also fail
    original_value, perturbed_value: numeric field perturbed (mm in history is cm;
                                     reconstruction engine ×10 → mm for KQP)
"""
from __future__ import annotations

import copy
import json
import math
import random
import string
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# History schema helpers
# ---------------------------------------------------------------------------

def parse_history(history: dict) -> tuple[dict | None, dict | None, dict]:
    """Return (sketch_entity, extrude_entity, refs).

    refs contains auxiliary references needed to round-trip modifications
    (consumed_profile_id, consumed_sketch_id, uuid_to_loops mapping).
    """
    entities = history.get("entities", {})
    timeline = history.get("timeline", [])
    sketch = extrude = None
    refs: dict[str, Any] = {"consumed_profile_id": None,
                              "consumed_sketch_id": None}

    for ev in timeline:
        eid = ev.get("entity")
        e = entities.get(eid, {})
        etype = e.get("type")
        if etype == "Sketch" and sketch is None:
            sketch = e
            refs["consumed_sketch_id"] = eid
        elif etype == "ExtrudeFeature" and extrude is None:
            extrude = e

    if extrude is not None:
        consumed = extrude.get("profiles", [])
        if consumed:
            refs["consumed_profile_id"] = consumed[0].get("profile")
            refs["consumed_sketch_id"] = consumed[0].get("sketch",
                                                        refs["consumed_sketch_id"])

    return sketch, extrude, refs


# ---------------------------------------------------------------------------
# Profile type detection (for sampler.py)
# ---------------------------------------------------------------------------

def detect_profile_type(history: dict) -> str:
    """Classify the EXTRUDE-consumed profile into one of:
       rectangle | rectangle_frame | circle | annulus | stadium |
       polygon_with_fillets | arbitrary_closed | unknown.

    Detection rules (mirrors DesignPlan Compiler v6 Stage 3.1):
      * annulus: outer is a circle, profile has >=1 inner loop
      * circle:  outer is a single circle, no inner loops
      * stadium: outer has 2 arcs + 2 lines (re-entrant rectangle)
      * rectangular_frame: outer is 4 lines + has >=1 inner loop
      * polygon_with_fillets: outer has >=4 lines AND >=1 inner loop AND outer line count > 4
      * rectangle: outer is 4 lines, no inner loops
      * arbitrary_closed: catch-all
    """
    sketch, _, refs = parse_history(history)
    if sketch is None:
        return "unknown"
    profile_id = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(profile_id)
    if profile is None:
        return "unknown"
    outer_loop = None
    inner_loops = []
    for loop in profile.get("loops", []):
        if loop.get("is_outer"):
            outer_loop = loop
        else:
            inner_loops.append(loop)
    if outer_loop is None:
        return "unknown"
    outer_curves = [sketch.get("curves", {}).get(pc.get("curve", ""))
                    for pc in outer_loop.get("profile_curves", [])]
    n_outer = len(outer_curves)
    n_inner = len(inner_loops)
    types = [c.get("type") if c else None for c in outer_curves]

    # Filter out None
    n_circles = sum(1 for t in types if t == "SketchCircle")
    n_arcs = sum(1 for t in types if t == "SketchArc")
    n_lines = sum(1 for t in types if t == "SketchLine")

    if n_circles == 1 and n_inner == 0 and n_outer == 1:
        return "circle"
    if n_outer == 2 and n_inner == 0:
        # Two SketchCircles in outer could mean arc-pair or bigger composite
        return "circle"  # treat as circle (should be rare)
    if n_circles >= 1 and n_inner >= 1:
        return "annulus"
    if n_lines == 4 and n_inner == 0:
        return "rectangle"
    if n_arcs == 2 and n_lines == 2 and n_inner == 0:
        return "stadium"
    if n_lines >= 4 and n_inner >= 1:
        # could be rectangular_frame or polygon_with_fillets
        if n_lines == 4:
            return "rectangular_frame"
        return "polygon_with_fillets"
    return "arbitrary_closed"


def detect_extent_type(history: dict) -> str:
    _, extrude, _ = parse_history(history)
    if extrude is None:
        return "unknown"
    et = extrude.get("extent_type", "")
    if et == "SymmetricFeatureExtentType":
        return "symmetric"
    elif et == "TwoSidesFeatureExtentType":
        return "two_sides"
    elif et == "OneSideFeatureExtentType":
        return "one_side"
    return et


# ---------------------------------------------------------------------------
# E1: Envelope / bbox dimension error
# ---------------------------------------------------------------------------

def op_E1_envelope(history: dict, design_plan: dict, *, axis: str = "u",
                    scale: float = 1.2) -> tuple[dict, dict, dict]:
    """Scale the outer profile along axis (u or v).

    Modifies history.points (which SketchLines reference). The reconstruction
    engine reads points[*].{x,y} directly so this correctly changes the bbox.
    """
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)

    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E1: no Sketch entity")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E1: no consumed profile")
    outer_loop = next((l for l in profile.get("loops", [])
                         if l.get("is_outer")), None)
    if outer_loop is None:
        raise ValueError("E1: no outer loop")
    points = sketch.get("points", {})

    # Compute centroid of outer loop
    xs, ys = [], []
    for pc in outer_loop.get("profile_curves", []):
        cid = pc.get("curve")
        c = sketch.get("curves", {}).get(cid, {})
        sp_id = c.get("start_point")
        ep_id = c.get("end_point")
        if sp_id and sp_id in points:
            xs.append(points[sp_id].get("x", 0))
            ys.append(points[sp_id].get("y", 0))
        if ep_id and ep_id in points:
            xs.append(points[ep_id].get("x", 0))
            ys.append(points[ep_id].get("y", 0))
    if not xs:
        raise ValueError("E1: no points to perturb")
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    # Mutate every point referenced by outer loop (and inner loops if axis=u)
    target_pt_ids = set()
    for pc in outer_loop.get("profile_curves", []):
        cid = pc.get("curve")
        c = sketch.get("curves", {}).get(cid, {})
        for k in ("start_point", "end_point"):
            pid_p = c.get(k)
            if pid_p:
                target_pt_ids.add(pid_p)

    for pt_id in target_pt_ids:
        pt = points.get(pt_id)
        if pt is None:
            continue
        if axis == "u":
            pt["x"] = cx + (pt["x"] - cx) * scale
        else:
            pt["y"] = cy + (pt["y"] - cy) * scale

    # Update design_plan bbox (best-effort; KQP will still detect mismatch)
    if "global_envelope" in design_plan and "bbox" in design_plan.get("global_envelope", {}):
        bbox = design_plan["global_envelope"]["bbox"]
        if axis in bbox:
            cur = bbox[axis].get("value", 0.0)
            if cur:
                bbox[axis]["value"] = abs(cur) * scale

    orig_w = (max(xs) - min(xs)) if axis == "u" else (max(ys) - min(ys))
    return history, design_plan, {
        "operator": "E1_envelope",
        "axis": axis,
        "scale": scale,
        "modified_history_field": "sketch.points[*].x|y",
        "source_design_plan_field": f"$.global_envelope.bbox.{axis}.value",
        "original_value": orig_w,
        "perturbed_value": orig_w * scale,
        "target_intent": "bbox_size",
        "error_category": "E1_envelope_dim",
        "expected_failed_query": [
            f"q_bbox_{axis}",
        ],
        "allowed_secondary_failed_queries": ["cylinder_radius", "through_void_count"],
    }


# ---------------------------------------------------------------------------
# E2: Extrude depth / thickness error
# ---------------------------------------------------------------------------

def op_E2_extrude_depth(history: dict, design_plan: dict, *,
                          scale: float = 1.5) -> tuple[dict, dict, dict]:
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    _, extrude, _ = parse_history(history)
    if extrude is None:
        raise ValueError("E2: no ExtrudeFeature")
    eo = extrude.get("extent_one")
    if not isinstance(eo, dict):
        raise ValueError("E2: no extent_one")
    orig = eo.get("distance", {}).get("value", 0.0)
    if orig == 0:
        # Fall back to one-sided-zero so we still have something to perturb
        orig = 1.0
    new = orig * scale
    eo["distance"]["value"] = new

    # Mirror in design_plan if present
    sb = design_plan.get("solid_bodies", [{}])[0]
    if "extrude" in sb and "distance_total" in sb["extrude"]:
        sb["extrude"]["distance_total"]["value"] = abs(new)
    if "dimensions" in sb and "extrude_distance" in sb["dimensions"]:
        sb["dimensions"]["extrude_distance"]["value"] = abs(new) * 10  # cm -> mm

    return history, design_plan, {
        "operator": "E2_extrude_depth",
        "scale": scale,
        "modified_history_field": "extrude.extent_one.distance.value",
        "source_design_plan_field": "$.solid_bodies[0].dimensions.extrude_distance.value",
        "original_value": orig,
        "perturbed_value": new,
        "target_intent": "bbox_size",
        "error_category": "E2_extrude_depth",
        "expected_failed_query": ["q_bbox_w"],
        "allowed_secondary_failed_queries": [
            "cylinder_radius", "through_void_count", "is_solid",
            "occt_valid", "symmetric_about_plane",
        ],
    }


# ---------------------------------------------------------------------------
# E3: Radius error (circle / annulus / stadium arc)
# ---------------------------------------------------------------------------

def op_E3_radius(history: dict, design_plan: dict, *,
                  scale: float = 1.25,
                  target: str = "outer",
                  ptype: str | None = None) -> tuple[dict, dict, dict]:
    """Scale circle/arc radius.

    Args:
        target: 'outer' (default), 'inner' (annulus inner), 'arc' (stadium arc).
        ptype: optional profile type override; otherwise detected from history.
    """
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E3: no Sketch entity")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E3: no consumed profile")

    if ptype is None:
        ptype = detect_profile_type(history)

    if ptype == "annulus":
        outer_loop = next((l for l in profile.get("loops", [])
                            if l.get("is_outer")), None)
        inner_loops = [l for l in profile.get("loops", [])
                       if not l.get("is_outer")]
        if target == "inner" and inner_loops:
            target_loop = inner_loops[0]
            kind = "inner"
        else:
            target_loop = outer_loop
            kind = "outer"
    elif ptype in ("circle", "stadium"):
        # Stadium: scale the arc radius; circle: scale the only circle.
        if ptype == "circle":
            target_loop = next((l for l in profile.get("loops", [])
                                if l.get("is_outer")), None)
            kind = "radius"
        else:
            # stadium: find outer loop with arcs
            outer_loop = next((l for l in profile.get("loops", [])
                                if l.get("is_outer")), None)
            target_loop = outer_loop
            kind = "arc"
    else:
        raise ValueError(f"E3: profile type {ptype} does not have a circle/arc to perturb")

    if target_loop is None:
        raise ValueError("E3: no target loop found")

    # Find the target curve
    target_curve_id = None
    orig_radius = None
    for pc in target_loop.get("profile_curves", []):
        cid = pc.get("curve")
        c = sketch.get("curves", {}).get(cid, {})
        ctype = c.get("type")
        if kind == "arc" and ctype == "SketchArc":
            target_curve_id = cid
            orig_radius = c.get("radius")
            break
        elif kind in ("outer", "inner", "radius") and ctype == "SketchCircle":
            target_curve_id = cid
            orig_radius = c.get("radius")
            break
    if target_curve_id is None:
        raise ValueError(f"E3: no target curve for kind={kind} on profile={ptype}")

    new_radius = orig_radius * scale
    # Ensure annulus inner radius remains strictly less than outer radius
    if ptype == "annulus" and kind == "inner":
        outer_radius = None
        for pc in next((l for l in profile.get("loops", [])
                         if l.get("is_outer")), []).get("profile_curves", []):
            c = sketch.get("curves", {}).get(pc.get("curve", ""), {})
            if c.get("type") == "SketchCircle":
                outer_radius = c.get("radius")
                break
        if outer_radius is not None and new_radius >= outer_radius:
            new_radius = outer_radius * 0.9

    sketch["curves"][target_curve_id]["radius"] = new_radius

    # Mirror to design_plan if applicable
    sb = design_plan.get("solid_bodies", [{}])[0]
    prof_in_dp = sb.get("profiles", [{}])[0]
    if ptype == "circle" and "radius" in prof_in_dp:
        prof_in_dp["radius"]["value"] = new_radius * 10  # cm -> mm
    elif ptype == "annulus":
        if kind == "outer" and "outer_radius" in prof_in_dp:
            prof_in_dp["outer_radius"]["value"] = new_radius * 10
        elif kind == "inner" and "inner_radius" in prof_in_dp:
            prof_in_dp["inner_radius"]["value"] = new_radius * 10

    return history, design_plan, {
        "operator": "E3_radius",
        "ptype": ptype,
        "radius_kind": kind,
        "scale": scale,
        "modified_history_field": f"sketch.curves[{target_curve_id}].radius",
        "source_design_plan_field": (
            f"$.solid_bodies[0].profiles[0].{kind}_radius.value"
            if ptype == "annulus" else "$.solid_bodies[0].profiles[0].radius.value"),
        "original_value": orig_radius,
        "perturbed_value": new_radius,
        "target_intent": "cylinder_radius",
        "error_category": "E3_radius",
        "expected_failed_query": [],   # filled at sampler time from kqp instance
        "allowed_secondary_failed_queries": [
            "bbox_size", "through_void_count", "is_solid", "occt_valid",
        ],
    }


# ---------------------------------------------------------------------------
# E4: Inner loop / void error
# ---------------------------------------------------------------------------

def op_E4_void_remove(history: dict, design_plan: dict,
                       *, which: int = 0) -> tuple[dict, dict, dict]:
    """Remove one inner loop from an annulus / rectangular_frame."""
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E4: no Sketch")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E4: no consumed profile")
    inner_loops = [(i, l) for i, l in enumerate(profile.get("loops", []))
                    if not l.get("is_outer")]
    if not inner_loops:
        raise ValueError("E4: no inner loops to remove")

    idx, target = inner_loops[min(which, len(inner_loops) - 1)]
    new_loops = [l for j, l in enumerate(profile["loops"]) if j != idx]
    profile["loops"] = new_loops

    # Design plan
    sb = design_plan.get("solid_bodies", [{}])[0]
    p0 = sb.get("profiles", [{}])[0]
    new_count = sum(1 for l in profile["loops"] if not l.get("is_outer"))
    if "inner_loop_count" in p0:
        p0["inner_loop_count"]["value"] = new_count

    return history, design_plan, {
        "operator": "E4_void_remove",
        "modified_history_field": (
            f"sketch.profiles[{pid}].loops[{idx}] (removed)"),
        "source_design_plan_field": "$.solid_bodies[0].profiles[0].inner_loop_count.value",
        "original_value": len(inner_loops),
        "perturbed_value": new_count,
        "target_intent": "through_void_count",
        "error_category": "E4_void",
        "expected_failed_query": ["q_void_count"],
        "allowed_secondary_failed_queries": ["bbox_size", "occt_valid", "is_solid"],
    }


def op_E4_void_add(history: dict, design_plan: dict) -> tuple[dict, dict, dict]:
    """Add an extra inner loop (SketchCircle) — produces more holes than designed."""
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E4: no Sketch")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E4: no consumed profile")
    outer = next((l for l in profile.get("loops", [])
                   if l.get("is_outer")), None)
    if outer is None:
        raise ValueError("E4: no outer loop")

    # Find centroid in cm from existing points.
    # Try start_point / end_point first, fall back to circle center_point.
    xs, ys = [], []
    points = sketch.get("points", {})
    for pc in outer.get("profile_curves", []):
        cid = pc.get("curve")
        c = sketch.get("curves", {}).get(cid, {})
        pts_ids = []
        for k in ("start_point", "end_point", "center_point"):
            v = c.get(k)
            if v:
                pts_ids.append(v)
        for pp_id in pts_ids:
            pp = points.get(pp_id)
            if pp is None:
                continue
            xs.append(pp["x"])
            ys.append(pp["y"])

    # Fallback: scan all points to get extents
    if not xs:
        for pp_id, pp in points.items():
            xs.append(pp.get("x", 0.0))
            ys.append(pp.get("y", 0.0))

    if not xs:
        # try to get centre from circle's center_point field
        for pc in outer.get("profile_curves", []):
            c = sketch.get("curves", {}).get(pc.get("curve", ""), {})
            ct = c.get("center_point", "")
            if ct:
                pp = points.get(ct)
                if pp:
                    xs = [pp["x"]] * 4
                    ys = [pp["y"]] * 4
                    break
    if not xs:
        # Last resort: scan any profile point
        if points:
            for v in points.values():
                xs.append(v.get("x", 0.0))
                ys.append(v.get("y", 0.0))
        else:
            raise ValueError("E4: no centroid available")

    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    r = (span_x + span_y) / 8 if (span_x + span_y) > 0 else 0.05

    # Generate unique ids
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    new_pid = f"perturbed_inner_pt_{rand}"
    new_cid = f"perturbed_inner_curve_{rand}"
    if "points" not in sketch:
        sketch["points"] = {}
    sketch["points"][new_pid] = {"type": "Point3D", "x": cx, "y": cy, "z": 0.0}
    sketch["curves"][new_cid] = {
        "type": "SketchCircle",
        "center_point": new_pid,
        "radius": r,
        "construction_geom": False,
        "fixed": False,
        "fully_constrained": False,
        "reference": False,
        "visible": True,
    }
    profile["loops"].append({
        "is_outer": False,
        "profile_curves": [{"type": "Line3D", "curve": new_cid}],
    })
    new_count = sum(1 for l in profile["loops"] if not l.get("is_outer"))

    sb = design_plan.get("solid_bodies", [{}])[0]
    p0 = sb.get("profiles", [{}])[0]
    if "inner_loop_count" in p0:
        p0["inner_loop_count"]["value"] = new_count

    return history, design_plan, {
        "operator": "E4_void_add",
        "modified_history_field": (
            f"sketch.profiles[{pid}].loops[new_inner]"),
        "source_design_plan_field": "$.solid_bodies[0].profiles[0].inner_loop_count.value",
        "original_value": new_count - 1,
        "perturbed_value": new_count,
        "target_intent": "through_void_count",
        "error_category": "E4_void",
        "expected_failed_query": ["q_void_count"],
        "allowed_secondary_failed_queries": ["bbox_size", "occt_valid", "is_solid"],
    }


# ---------------------------------------------------------------------------
# E5: Extent type (symmetric → one_side)
# ---------------------------------------------------------------------------

def op_E5_extent_type(history: dict, design_plan: dict) -> tuple[dict, dict, dict]:
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    _, extrude, _ = parse_history(history)
    if extrude is None:
        raise ValueError("E5: no extrude")
    orig_et = extrude.get("extent_type")
    if orig_et != "SymmetricFeatureExtentType":
        raise ValueError(f"E5: extent_type is {orig_et!r}, not Symmetric")

    extrude["extent_type"] = "OneSideFeatureExtentType"
    # Keep distance but axis now extends one-sided
    sb = design_plan.get("solid_bodies", [{}])[0]
    if "extrude" in sb:
        sb["extrude"]["extent_type"] = "one_side"
        sb["extrude"]["direction"] = "+w"
    # dim distance_total: now only one side, so it equals distance (was 2x)
    eo = extrude.get("extent_one", {})
    if isinstance(eo, dict):
        dval = eo.get("distance", {}).get("value", 0.0)
        if dval and "dimensions" in sb and "extrude_distance" in sb["dimensions"]:
            # old bbox_w = 2 * dval; new bbox_w = dval
            sb["dimensions"]["extrude_distance"]["value"] = abs(dval) * 10

    return history, design_plan, {
        "operator": "E5_extent_type",
        "modified_history_field": "extrude.extent_type",
        "source_design_plan_field": "$.solid_bodies[0].extrude.extent_type",
        "original_value": orig_et,
        "perturbed_value": "OneSideFeatureExtentType",
        "target_intent": "symmetric_about_plane",
        "error_category": "E5_extent_type",
        "expected_failed_query": [
            "q_bbox_w",   # bbox_w shrinks (2x → 1x distance)
            "q_symmetric_about_plane",  # also likely fail
        ],
        "allowed_secondary_failed_queries": ["is_solid", "occt_valid"],
    }


# ---------------------------------------------------------------------------
# E6: Validity / solid error
# ---------------------------------------------------------------------------

def op_E6_zero_extrude(history: dict, design_plan: dict) -> tuple[dict, dict, dict]:
    """Set extrude distance to 0 — produces a degenerate (zero-thickness) body."""
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    _, extrude, _ = parse_history(history)
    if extrude is None:
        raise ValueError("E6: no extrude")
    eo = extrude.get("extent_one")
    if not isinstance(eo, dict) or "distance" not in eo:
        raise ValueError("E6: no extent_one.distance")
    orig = eo["distance"]["value"]
    eo["distance"]["value"] = 0.0

    sb = design_plan.get("solid_bodies", [{}])[0]
    if "dimensions" in sb and "extrude_distance" in sb["dimensions"]:
        sb["dimensions"]["extrude_distance"]["value"] = 0.0

    return history, design_plan, {
        "operator": "E6_zero_extrude",
        "modified_history_field": "extrude.extent_one.distance.value",
        "source_design_plan_field": "$.solid_bodies[0].dimensions.extrude_distance.value",
        "original_value": orig,
        "perturbed_value": 0.0,
        "target_intent": "is_solid",
        "error_category": "E6_validity",
        "expected_failed_query": ["q_is_solid", "q_occt_valid", "q_bbox_w"],
        "allowed_secondary_failed_queries": ["body_count", "cylinder_radius"],
    }


def op_E6_zero_radius(history: dict, design_plan: dict) -> tuple[dict, dict, dict]:
    """Set the outer (or only) circle radius to 0 — degenerate circle."""
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E6: no sketch")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E6: no profile")
    outer = next((l for l in profile.get("loops", [])
                   if l.get("is_outer")), None)
    if outer is None:
        raise ValueError("E6: no outer")
    target = None
    orig_r = None
    for pc in outer.get("profile_curves", []):
        c = sketch.get("curves", {}).get(pc.get("curve", ""), {})
        if c.get("type") == "SketchCircle":
            target = pc.get("curve")
            orig_r = c.get("radius")
            break
    if target is None:
        raise ValueError("E6: no outer circle")
    sketch["curves"][target]["radius"] = 0.0

    sb = design_plan.get("solid_bodies", [{}])[0]
    p0 = sb.get("profiles", [{}])[0]
    if "radius" in p0:
        p0["radius"]["value"] = 0.0
    elif "outer_radius" in p0:
        p0["outer_radius"]["value"] = 0.0

    return history, design_plan, {
        "operator": "E6_zero_radius",
        "modified_history_field": f"sketch.curves[{target}].radius",
        "source_design_plan_field": "$.solid_bodies[0].profiles[0].radius.value",
        "original_value": orig_r,
        "perturbed_value": 0.0,
        "target_intent": "is_solid",
        "error_category": "E6_validity",
        "expected_failed_query": ["q_is_solid", "q_occt_valid"],
        "allowed_secondary_failed_queries": ["cylinder_radius", "bbox_size"],
    }


def op_E6_inner_gt_outer(history: dict, design_plan: dict) -> tuple[dict, dict, dict]:
    """Annulus: make inner radius > outer radius — invalid geometry."""
    history = copy.deepcopy(history)
    design_plan = copy.deepcopy(design_plan)
    sketch, _, refs = parse_history(history)
    if sketch is None:
        raise ValueError("E6: no sketch")
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        raise ValueError("E6: no profile")
    outer_loop = next((l for l in profile.get("loops", [])
                        if l.get("is_outer")), None)
    inner_loops = [l for l in profile.get("loops", [])
                    if not l.get("is_outer")]
    if not (outer_loop and inner_loops):
        raise ValueError("E6: not annulus-shaped")

    outer_c = None
    for pc in outer_loop.get("profile_curves", []):
        c = sketch.get("curves", {}).get(pc.get("curve", ""), {})
        if c.get("type") == "SketchCircle":
            outer_c = c
            break
    inner_c = None
    inner_pc = None
    for pc in inner_loops[0].get("profile_curves", []):
        c = sketch.get("curves", {}).get(pc.get("curve", ""), {})
        if c.get("type") == "SketchCircle":
            inner_c = c
            inner_pc = pc
            break
    if not (outer_c and inner_c):
        raise ValueError("E6: missing circles")
    orig_outer = outer_c.get("radius", 0)
    orig_inner = inner_c.get("radius", 0)
    # Swap: inner = outer + 0.5
    new_inner = orig_outer + 0.5
    inner_c["radius"] = new_inner

    sb = design_plan.get("solid_bodies", [{}])[0]
    p0 = sb.get("profiles", [{}])[0]
    if "inner_radius" in p0:
        p0["inner_radius"]["value"] = new_inner * 10

    return history, design_plan, {
        "operator": "E6_inner_gt_outer",
        "modified_history_field": f"sketch.curves[{inner_pc['curve']}].radius",
        "source_design_plan_field": "$.solid_bodies[0].profiles[0].inner_radius.value",
        "original_value": orig_inner,
        "perturbed_value": new_inner,
        "target_intent": "is_solid",
        "error_category": "E6_validity",
        "expected_failed_query": ["q_occt_valid", "q_is_solid"],
        "allowed_secondary_failed_queries": ["cylinder_radius", "through_void_count"],
    }


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def all_operators() -> dict:
    """Return mapping perturbation_type -> function (history, design_plan, **kw)."""
    return {
        "E1_envelope_u": lambda h, dp: op_E1_envelope(h, dp, axis="u", scale=1.20),
        "E1_envelope_v": lambda h, dp: op_E1_envelope(h, dp, axis="v", scale=1.20),
        "E1_envelope_u_shrink": lambda h, dp: op_E1_envelope(h, dp, axis="u", scale=0.80),
        "E1_envelope_v_shrink": lambda h, dp: op_E1_envelope(h, dp, axis="v", scale=0.80),
        "E2_extrude_deep": lambda h, dp: op_E2_extrude_depth(h, dp, scale=1.5),
        "E2_extrude_shallow": lambda h, dp: op_E2_extrude_depth(h, dp, scale=0.5),
        "E3_radius_up": lambda h, dp: op_E3_radius(h, dp, scale=1.25, target="outer"),
        "E3_radius_down": lambda h, dp: op_E3_radius(h, dp, scale=0.75, target="outer"),
        "E3_inner_radius_up": lambda h, dp: op_E3_radius(h, dp, scale=1.30, target="inner"),
        "E3_inner_radius_down": lambda h, dp: op_E3_radius(h, dp, scale=0.70, target="inner"),
        "E4_void_remove_one": lambda h, dp: op_E4_void_remove(h, dp, which=0),
        "E4_void_add": lambda h, dp: op_E4_void_add(h, dp),
        "E5_extent_type_change": lambda h, dp: op_E5_extent_type(h, dp),
        "E6_zero_extrude": lambda h, dp: op_E6_zero_extrude(h, dp),
        "E6_zero_radius": lambda h, dp: op_E6_zero_radius(h, dp),
        "E6_inner_gt_outer": lambda h, dp: op_E6_inner_gt_outer(h, dp),
    }
