"""Deterministic Design Plan Compiler.

Converts a Fusion360 Gallery modeling-history JSON into a v0.4 Design Plan.

Implements the 6-stage design from doc/04_建模序列JSON到DesignPlan确定性Compiler设计.md
plus the P0/P1 fixes from doc/complier可行性验证-样本10-20.md:
  - Stage 1: parse + float cleanup (coords cleaned; unit vectors length-normalized only)
  - Stage 2: dependency graph + ISOLATED SKETCH DETECTION (auxiliary_geometry)
  - Stage 3.1: profile shape recognition (rectangle/circle/annulus/stadium/
               polygon_with_fillets/rectangular_frame/arbitrary_closed)
               + MULTI-PROFILE single extrude support
  - Stage 3.2: dimension extraction (3 sources: explicit_dimension /
               inferred_from_point_span / curve_field)
               + size vs positioning dim distinction
  - Stage 3.3: extrude params (incl. NEGATIVE extrude -> direction + magnitude)
  - Stage 3.4: frame (u/v/w from reference_plane; plane.origin DISCARDED)
  - Stage 4: part_category (quantified rules) + constraints (structured,
             incl. implicit concentricity + coincident_inert)
  - Stage 5: validation_intents (span_along_frame_axis, surface_type_distribution,
             through_void_count, etc.)
  - Stage 6: output v0.4 JSON

Unit convention: source JSON geometry values are in cm; Design Plan uses mm (x10).
See doc/04 §8.2 unit trap.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any

UNIT_SCALE = 10.0  # cm -> mm
FLOAT_ZERO_TOL = 1e-9
FLOAT_ROUND_TOL = 1e-6
ORTHO_TOL = 1e-6
PARALLEL_TOL = 1e-6


# ---------------------------------------------------------------------------
# Stage 1: parse + cleanup
# ---------------------------------------------------------------------------

def clean_coord(v: float) -> float:
    """Clean a coordinate value: snap near-zero to 0, near-integer to integer."""
    if v is None:
        return 0.0
    if abs(v) < FLOAT_ZERO_TOL:
        return 0.0
    r = round(v)
    if abs(v - r) < FLOAT_ROUND_TOL:
        return float(r)
    return float(v)


def clean_unit_vec_component(v: float) -> float:
    """Clean a unit-vector component: snap near-zero to 0, but do NOT round to
    integer (would corrupt rotated frames like sample 20's 0.0049)."""
    if v is None:
        return 0.0
    if abs(v) < FLOAT_ZERO_TOL:
        return 0.0
    return float(v)


def normalize_vec3(x: float, y: float, z: float) -> list[float]:
    """Length-normalize a 3-vector; return [x,y,z]. For zero-length, return [0,0,0]."""
    n = math.sqrt(x * x + y * y + z * z)
    if n < FLOAT_ZERO_TOL:
        return [0.0, 0.0, 0.0]
    return [x / n, y / n, z / n]


def vec_from_dict(d: dict) -> tuple[float, float, float]:
    return (d.get("x", 0.0), d.get("y", 0.0), d.get("z", 0.0))


def dot3(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross3(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dist3(a, b) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


# ---------------------------------------------------------------------------
# Stage 2: dependency graph + isolated sketch detection
# ---------------------------------------------------------------------------

def build_dependency_graph(data: dict) -> dict:
    """Return {sketches: [...], extrudes: [...], unused_sketch_ids: [...]}.

    A sketch is 'used' if any extrude.profiles[].sketch references it.
    """
    entities = data.get("entities", {})
    timeline = data.get("timeline", [])

    sketches = []
    extrudes = []
    for ev in timeline:
        eid = ev.get("entity")
        e = entities.get(eid, {})
        etype = e.get("type")
        if etype == "Sketch":
            sketches.append({"id": eid, "entity": e})
        elif etype == "ExtrudeFeature":
            extrudes.append({"id": eid, "entity": e})
        # other types ignored for now (Revolve, Fillet, etc.)

    used_sketch_ids = set()
    for ex in extrudes:
        for prof in ex["entity"].get("profiles", []):
            used_sketch_ids.add(prof.get("sketch"))

    unused = [s["id"] for s in sketches if s["id"] not in used_sketch_ids]
    return {"sketches": sketches, "extrudes": extrudes, "unused_sketch_ids": unused}


# ---------------------------------------------------------------------------
# Stage 3.1: profile shape recognition
# ---------------------------------------------------------------------------

def classify_profile(sketch_entity: dict, profile_id: str) -> dict:
    """Classify a single profile into a v0.4 profile dict.

    Returns {type, rings: [{role, loop_type, curve_count, curves: [...]}]}.
    """
    profile = sketch_entity.get("profiles", {}).get(profile_id)
    if profile is None:
        return {"type": "arbitrary_closed", "rings": [], "_error": "profile not found"}

    loops = profile.get("loops", [])
    points = sketch_entity.get("points", {})
    curves = sketch_entity.get("curves", {})

    rings = []
    for loop in loops:
        is_outer = loop.get("is_outer", False)
        role = "outer" if is_outer else "inner"
        pcurves = loop.get("profile_curves", [])
        ring_curves = []
        loop_curve_types = []
        for pc in pcurves:
            cid = pc.get("curve")
            c = curves.get(cid, {})
            ctype = c.get("type")
            loop_curve_types.append(ctype)
            if ctype == "SketchLine":
                sp = points.get(c.get("start_point"), {})
                ep = points.get(c.get("end_point"), {})
                ring_curves.append({
                    "kind": "line", "ref": None,
                    "start_uv": [clean_coord(sp.get("x", 0)), clean_coord(sp.get("y", 0))],
                    "end_uv": [clean_coord(ep.get("x", 0)), clean_coord(ep.get("y", 0))],
                })
            elif ctype == "SketchCircle":
                ctr = points.get(c.get("center_point"), {})
                ring_curves.append({
                    "kind": "circle", "ref": None,
                    "center_uv": [clean_coord(ctr.get("x", 0)), clean_coord(ctr.get("y", 0))],
                    "radius": clean_coord(c.get("radius", 0)),
                })
            elif ctype == "SketchArc":
                ctr = points.get(c.get("center_point"), {})
                ring_curves.append({
                    "kind": "arc", "ref": None,
                    "center_uv": [clean_coord(ctr.get("x", 0)), clean_coord(ctr.get("y", 0))],
                    "radius": clean_coord(c.get("radius", 0)),
                    "start_angle_deg": math.degrees(c.get("start_angle", 0)),
                    "end_angle_deg": math.degrees(c.get("end_angle", 0)),
                })
        rings.append({
            "role": role,
            "loop_type": _loop_type_name(loop_curve_types),
            "curve_count": len(ring_curves),
            "curves": ring_curves,
            "_curve_types": loop_curve_types,
        })

    # Sort rings: outer first, then inner. Fusion360 loop order is NOT guaranteed
    # to put outer first (sample 29 has inner as loop 0). Sort by role for stability.
    rings.sort(key=lambda r: 0 if r["role"] == "outer" else 1)

    ptype = _classify_type(rings)
    return {"type": ptype, "rings": rings}


def _loop_type_name(curve_types: list[str]) -> str:
    has_line = "SketchLine" in curve_types
    has_arc = "SketchArc" in curve_types
    has_circle = "SketchCircle" in curve_types
    if has_circle and not has_line and not has_arc:
        return "circle"
    if has_line and not has_arc and not has_circle:
        return "polyline"
    return "composite_line_arc"


def _classify_type(rings: list[dict]) -> str:
    """Recognize profile.type from rings structure."""
    if not rings:
        return "arbitrary_closed"
    outer = rings[0]
    inner_rings = rings[1:]
    outer_curves = outer["curves"]
    outer_types = outer["_curve_types"]

    # annulus: 2 rings, each a single circle, concentric
    if len(rings) == 2 and all(r["loop_type"] == "circle" and r["curve_count"] == 1 for r in rings):
        return "annulus"

    # circle: 1 ring, single circle
    if len(rings) == 1 and outer["loop_type"] == "circle" and outer["curve_count"] == 1:
        return "circle"

    # rectangular_frame: 2 rings, both polyline with 4 lines, both rectangles
    if (len(rings) == 2 and outer["loop_type"] == "polyline" and outer["curve_count"] == 4
            and inner_rings[0]["loop_type"] == "polyline" and inner_rings[0]["curve_count"] == 4
            and _is_rectangle(outer_curves) and _is_rectangle(inner_rings[0]["curves"])):
        return "rectangular_frame"

    # rectangle: 1 ring, 4 lines, orthogonal
    if len(rings) == 1 and outer["loop_type"] == "polyline" and outer["curve_count"] == 4 and _is_rectangle(outer_curves):
        return "rectangle"

    # stadium: outer ring = 2 arcs + 2 lines, arcs equal radius semicircles, lines parallel.
    # Inner rings (holes) are ALLOWED (sample 25 = stadium with 2 holes).
    if (outer["loop_type"] == "composite_line_arc"
            and outer_types.count("SketchArc") == 2 and outer_types.count("SketchLine") == 2):
        if _is_stadium(outer_curves):
            return "stadium"

    # polygon_with_fillets: outer has line+arc mix forming a polygon (≥3 lines)
    # with arcs as corner fillets. Sample 37 (2 lines + 2 unequal arcs) is NOT
    # this (only 2 lines can't form a polygon) -> falls to arbitrary_closed.
    if (outer["loop_type"] == "composite_line_arc" and "SketchArc" in outer_types
            and outer_types.count("SketchLine") >= 3):
        return "polygon_with_fillets"

    return "arbitrary_closed"


def _is_rectangle(curves: list[dict]) -> bool:
    """Check if 4 line curves form an orthogonal rectangle (2 parallel pairs, perpendicular)."""
    if len(curves) != 4 or not all(c["kind"] == "line" for c in curves):
        return False
    dirs = []
    for c in curves:
        d = sub3(tuple(c["end_uv"]) + (0,), tuple(c["start_uv"]) + (0,))
        n = math.sqrt(d[0] ** 2 + d[1] ** 2)
        if n < FLOAT_ZERO_TOL:
            return False
        dirs.append((d[0] / n, d[1] / n, 0.0))
    # group by parallel (|dot|~1)
    groups = []
    for d in dirs:
        placed = False
        for g in groups:
            if abs(abs(dot3(d, g[0])) - 1.0) < PARALLEL_TOL:
                g.append(d)
                placed = True
                break
        if not placed:
            groups.append([d])
    if len(groups) != 2:
        return False
    if len(groups[0]) != 2 or len(groups[1]) != 2:
        return False
    # groups must be perpendicular
    return abs(dot3(groups[0][0], groups[1][0])) < ORTHO_TOL


def _is_stadium(curves: list[dict]) -> bool:
    """Check if 2 arcs + 2 lines form a stadium (arcs equal radius, semicircle, lines parallel)."""
    arcs = [c for c in curves if c["kind"] == "arc"]
    lines = [c for c in curves if c["kind"] == "line"]
    if len(arcs) != 2 or len(lines) != 2:
        return False
    if abs(arcs[0]["radius"] - arcs[1]["radius"]) > FLOAT_ROUND_TOL:
        return False
    # arcs should be semicircles (angle span ~ pi)
    for a in arcs:
        span = abs(a["end_angle_deg"] - a["start_angle_deg"])
        if abs(span - 180.0) > 1.0:
            return False
    # lines parallel
    d0 = sub3(tuple(lines[0]["end_uv"]) + (0,), tuple(lines[0]["start_uv"]) + (0,))
    d1 = sub3(tuple(lines[1]["end_uv"]) + (0,), tuple(lines[1]["start_uv"]) + (0,))
    n0 = math.sqrt(d0[0] ** 2 + d0[1] ** 2)
    n1 = math.sqrt(d1[0] ** 2 + d1[1] ** 2)
    if n0 < FLOAT_ZERO_TOL or n1 < FLOAT_ZERO_TOL:
        return False
    d0 = (d0[0] / n0, d0[1] / n0, 0.0)
    d1 = (d1[0] / n1, d1[1] / n1, 0.0)
    return abs(abs(dot3(d0, d1)) - 1.0) < PARALLEL_TOL


# ---------------------------------------------------------------------------
# Stage 3.2: dimension extraction
# ---------------------------------------------------------------------------

def extract_dimensions(sketch_entity: dict, profile_class: dict, extrude_entity: dict, extrude_block: dict = None) -> dict:
    """Extract v0.4 dimensions block.

    v0.6: if extrude_block is provided, REUSE its distance_total as extrude_distance
    (single source of truth). Eliminates dual-computation inconsistency.
    """
    dims = {}
    warnings = []

    # extrude distance -- v0.6: single source (reuse extrude_block.distance_total)
    if extrude_block is not None and "distance_total" in extrude_block:
        dt = extrude_block["distance_total"]
        dims["extrude_distance"] = {
            "value": dt["value"],
            "tol": dt.get("tol", 0.01),
            "tol_kind": dt.get("tol_kind", "absolute"),
            "relative_tol": 1e-4,  # v0.6 NEW
            "source": dt.get("source", "explicit_dimension"),
        }
    else:
        # fallback (legacy path without extrude_block)
        extent_one = extrude_entity.get("extent_one", {})
        raw_dist = extent_one.get("distance", {}).get("value", 0.0)
        dims["extrude_distance"] = {
            "value": round(abs(raw_dist) * UNIT_SCALE, 6),
            "tol": 0.01, "tol_kind": "absolute", "relative_tol": 1e-4,
            "source": "explicit_dimension" if raw_dist != 0 else "inferred_from_point_span",
        }

    # per-profile params
    profile_dims_list = []
    for ring_set in [profile_class]:  # single profile per call; multi-profile handled by caller
        ptype = ring_set["type"]
        pd = _profile_type_dims(ptype, ring_set["rings"], sketch_entity)
        profile_dims_list.append(pd)
    dims["profiles"] = profile_dims_list

    return dims, warnings


def _profile_type_dims(ptype: str, rings: list[dict], sketch_entity: dict) -> dict:
    """Type-specific dimension params."""
    dims: dict[str, Any] = {}
    explicit_dims = sketch_entity.get("dimensions", {})

    if ptype == "rectangle":
        length_u, width_v, lu_src, wv_src = _rectangle_dims(rings[0]["curves"], explicit_dims, sketch_entity)
        dims["length_u"] = {"value": length_u, "tol": 0.01, "tol_kind": "absolute", "source": lu_src}
        dims["width_v"] = {"value": width_v, "tol": 0.01, "tol_kind": "absolute", "source": wv_src}

    elif ptype == "circle":
        radius, src = _circle_radius(rings[0]["curves"][0], explicit_dims)
        dims["radius"] = {"value": radius, "tol": 0.01, "tol_kind": "absolute", "source": src}
        # v0.5: center_uv (part-local, relative to sketch origin)
        ctr = rings[0]["curves"][0].get("center_uv", [0, 0])
        dims["center_uv"] = [round(c * UNIT_SCALE, 6) for c in ctr]

    elif ptype == "annulus":
        # v0.5 FIX: outer ring gets LARGER diameter, inner ring gets SMALLER.
        # v0.4 bug: both rings picked the same first Diameter dim.
        outer_r, src_o = _circle_radius(rings[0]["curves"][0], explicit_dims, prefer_larger=True)
        inner_r, src_i = _circle_radius(rings[1]["curves"][0], explicit_dims, prefer_smaller=True)
        # fallback: if explicit dims absent/ambiguous, use curve.radius directly
        if outer_r <= inner_r:
            outer_r = max(rings[0]["curves"][0].get("radius", 0), rings[1]["curves"][0].get("radius", 0)) * UNIT_SCALE
            inner_r = min(rings[0]["curves"][0].get("radius", 0), rings[1]["curves"][0].get("radius", 0)) * UNIT_SCALE
        dims["outer_radius"] = {"value": round(outer_r, 6), "tol": 0.01, "tol_kind": "absolute", "source": src_o}
        dims["inner_radius"] = {"value": round(inner_r, 6), "tol": 0.01, "tol_kind": "absolute", "source": src_i}
        ctr = rings[0]["curves"][0].get("center_uv", [0, 0])
        dims["center_uv"] = [round(c * UNIT_SCALE, 6) for c in ctr]

    elif ptype == "stadium":
        arcs = [c for c in rings[0]["curves"] if c["kind"] == "arc"]
        radius = arcs[0]["radius"] * UNIT_SCALE if arcs else 0.0
        # straight_length = distance between arc centers
        if len(arcs) == 2:
            c0 = arcs[0]["center_uv"]
            c1 = arcs[1]["center_uv"]
            straight = math.dist(c0, c1) * UNIT_SCALE
        else:
            straight = 0.0
        dims["straight_length"] = {"value": round(straight, 6), "tol": 0.01, "tol_kind": "absolute",
                                    "source": "inferred_from_point_span"}
        # radius source: try explicit Diameter dim, else curve_field
        r_src = "curve_field"
        for d in explicit_dims.values():
            if "Diameter" in (d.get("parameter", {}).get("role") or ""):
                r_src = "explicit_dimension"
                break
        dims["radius"] = {"value": round(radius, 6), "tol": 0.01, "tol_kind": "absolute", "source": r_src}

    elif ptype == "rectangular_frame":
        outer = rings[0]["curves"]
        inner = rings[1]["curves"]
        ol, ow, _, _ = _rectangle_dims(outer, {}, sketch_entity)
        il, iw, _, _ = _rectangle_dims(inner, {}, sketch_entity)
        dims["outer_length_u"] = {"value": ol, "tol": 0.01, "tol_kind": "absolute", "source": "inferred_from_point_span"}
        dims["outer_width_v"] = {"value": ow, "tol": 0.01, "tol_kind": "absolute", "source": "inferred_from_point_span"}
        dims["inner_length_u"] = {"value": il, "tol": 0.01, "tol_kind": "absolute", "source": "inferred_from_point_span"}
        dims["inner_width_v"] = {"value": iw, "tol": 0.01, "tol_kind": "absolute", "source": "inferred_from_point_span"}

    elif ptype == "polygon_with_fillets":
        lines = [c for c in rings[0]["curves"] if c["kind"] == "line"]
        arcs = [c for c in rings[0]["curves"] if c["kind"] == "arc"]
        side_lengths = [{"value": round(math.dist(tuple(c["start_uv"]), tuple(c["end_uv"])) * UNIT_SCALE, 6),
                         "source": "inferred_from_point_span"} for c in lines]
        fillet_radii = [{"value": round(c["radius"] * UNIT_SCALE, 6), "source": "curve_field"} for c in arcs]
        hole_radii = []
        for r in rings[1:]:
            for c in r["curves"]:
                if c["kind"] == "circle":
                    hole_radii.append({"value": round(c["radius"] * UNIT_SCALE, 6), "source": "curve_field"})
        dims["side_lengths"] = side_lengths
        dims["fillet_radii"] = fillet_radii
        dims["hole_radii"] = hole_radii

    elif ptype == "arbitrary_closed":
        # v0.5 NEW: generic dimension extraction for arbitrary_closed profiles.
        # Captures all arc radii (curve_field), line lengths (point_span),
        # circle radii (curve_field) without type-specific recognition.
        all_curves = []
        for r in rings:
            all_curves.extend(r["curves"])
        arc_radii = [{"value": round(c["radius"] * UNIT_SCALE, 6), "source": "curve_field"}
                     for c in all_curves if c["kind"] == "arc"]
        line_lengths = [{"value": round(math.dist(tuple(c["start_uv"]), tuple(c["end_uv"])) * UNIT_SCALE, 6),
                         "source": "inferred_from_point_span"}
                        for c in all_curves if c["kind"] == "line"]
        circle_radii = [{"value": round(c["radius"] * UNIT_SCALE, 6), "source": "curve_field"}
                        for c in all_curves if c["kind"] == "circle"]
        dims["curve_count"] = len(all_curves)
        dims["arc_radii"] = arc_radii
        dims["line_lengths"] = line_lengths
        dims["circle_radii"] = circle_radii

    return dims


def _rectangle_dims(curves, explicit_dims, sketch_entity) -> tuple:
    """Return (length_u_mm, width_v_mm, length_source, width_source)."""
    # try explicit Linear dims (Horizontal -> u, Vertical -> v)
    length_val = width_val = None
    for d in explicit_dims.values():
        if d.get("is_driving") is False:
            continue
        param = d.get("parameter", {})
        role = param.get("role") or ""
        orient = d.get("orientation")
        if "Linear" not in role:
            continue
        val = param.get("value", 0) * UNIT_SCALE
        if orient == "HorizontalDimensionOrientation":
            length_val = val
        elif orient == "VerticalDimensionOrientation":
            width_val = val
    # fallback: point span
    if length_val is None or width_val is None:
        pts = []
        for c in curves:
            pts.append(tuple(c["start_uv"]))
            pts.append(tuple(c["end_uv"]))
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            span_u = (max(xs) - min(xs)) * UNIT_SCALE
            span_v = (max(ys) - min(ys)) * UNIT_SCALE
            if length_val is None:
                length_val = round(span_u, 6)
            if width_val is None:
                width_val = round(span_v, 6)
    lu_src = "explicit_dimension" if any(d.get("orientation") == "HorizontalDimensionOrientation" for d in explicit_dims.values()) else "inferred_from_point_span"
    wv_src = "explicit_dimension" if any(d.get("orientation") == "VerticalDimensionOrientation" for d in explicit_dims.values()) else "inferred_from_point_span"
    return round(length_val, 6), round(width_val, 6), lu_src, wv_src


def _circle_radius(curve, explicit_dims, prefer_smaller=False, prefer_larger=False) -> tuple:
    """Return (radius_mm, source). Try explicit Diameter/Radial dim, else curve_field.

    v0.5 FIX: when multiple Diameter dims exist (annulus), pick the one matching
    prefer_smaller/prefer_larger instead of always taking the first. This fixes
    the bug where both annulus rings got the same (first) diameter.
    """
    radius_cm = curve.get("radius", 0)
    # collect ALL explicit Diameter/Radial values
    candidates = []  # list of (radius_cm, source)
    for d in explicit_dims.values():
        if d.get("is_driving") is False:
            continue
        param = d.get("parameter", {})
        role = param.get("role") or ""
        val = param.get("value", 0)
        if "Diameter" in role:
            candidates.append((val / 2.0, "explicit_dimension"))
        elif "Radial" in role:
            candidates.append((val, "explicit_dimension"))
    if candidates:
        if prefer_smaller:
            best_val, best_src = min(candidates, key=lambda x: x[0])
        elif prefer_larger:
            best_val, best_src = max(candidates, key=lambda x: x[0])
        else:
            best_val, best_src = candidates[0]
    else:
        best_val = radius_cm
        best_src = "curve_field"
    return round(best_val * UNIT_SCALE, 6), best_src


# ---------------------------------------------------------------------------
# Stage 3.3: extrude params (incl. negative direction)
# ---------------------------------------------------------------------------

def extract_extrude(extrude_entity: dict, properties: dict = None) -> dict:
    """v0.5: handles symmetric, degenerate_two_side, and direction cross-validation."""
    extent_type_raw = extrude_entity.get("extent_type", "")
    extent_one = extrude_entity.get("extent_one", {})
    raw_dist = extent_one.get("distance", {}).get("value", 0.0)
    e2_val = extrude_entity.get("extent_two", {}).get("distance", {}).get("value", 0.0) if extrude_entity.get("extent_two") else 0.0

    if "Symmetric" in extent_type_raw:
        # v0.5 NEW: SymmetricFeatureExtentType. extent_one.distance is HALF-length;
        # total = 2 * half. Body straddles plane.
        etype = "symmetric"
        direction = "both_symmetric"
        total = 2 * abs(raw_dist)
    elif "TwoSides" in extent_type_raw:
        # v0.5 NEW: detect degenerate (extent_two == 0) -> effectively one_side
        if abs(e2_val) < FLOAT_ROUND_TOL:
            etype = "degenerate_two_side"
            direction = "-w" if raw_dist < 0 else "+w"
            total = abs(raw_dist)
        elif abs(raw_dist - e2_val) < FLOAT_ROUND_TOL:
            etype = "symmetric"  # equal two-side == symmetric
            direction = "both_symmetric"
            total = abs(raw_dist) + abs(e2_val)
        else:
            etype = "two_side"
            direction = "both_asymmetric"
            total = abs(raw_dist) + abs(e2_val)
    elif "OneSide" in extent_type_raw:
        etype = "one_side"
        direction = "-w" if raw_dist < 0 else "+w"
        total = abs(raw_dist)
    else:
        etype = "one_side"
        direction = "-w" if raw_dist < 0 else "+w"
        total = abs(raw_dist)

    # v0.5 NEW: direction cross-validation against GT bbox w-axis span.
    # Catches cases where source distance is positive but body extends in -w
    # (sample 36: distance=+0.036 but bbox z in [-0.036, 0]).
    direction_verified = None
    if properties is not None and etype in ("one_side", "degenerate_two_side"):
        bbox = properties.get("bounding_box", {})
        mn = bbox.get("min_point", {})
        mx = bbox.get("max_point", {})
        # We don't have the frame here; approximate by checking each axis for a
        # one-sided span starting at 0 vs ending at 0. If an axis has min<0 and max~0,
        # the body extends in the negative direction along that axis.
        # This is a heuristic; the authoritative check needs the frame (done in caller).
        for ax in ("x", "y", "z"):
            lo, hi = mn.get(ax, 0), mx.get(ax, 0)
            if abs(hi) < FLOAT_ROUND_TOL and lo < -FLOAT_ROUND_TOL:
                # body extends in -axis; if this axis matches w_dir, direction should be -w
                direction_verified = "needs_frame_check"
                break

    op_raw = extrude_entity.get("operation", "")
    op_map = {"NewBodyFeatureOperation": "new_body", "JoinFeatureOperation": "join",
              "CutFeatureOperation": "cut", "IntersectFeatureOperation": "intersect"}
    operation = op_map.get(op_raw, "new_body")

    taper = extent_one.get("taper_angle", {}).get("value", 0.0)

    return {
        "extent_type": etype,
        "direction": direction,
        "distance_total": {"value": round(total * UNIT_SCALE, 6), "tol": 0.01, "tol_kind": "absolute",
                            "source": "explicit_dimension"},
        "operation": operation,
        "taper_angle_deg": {"value": round(taper, 6), "tol": 0.01, "tol_kind": "absolute"},
        "direction_verified": direction_verified if direction_verified else True,
    }


# ---------------------------------------------------------------------------
# Stage 3.4: frame extraction
# ---------------------------------------------------------------------------

def extract_frame(sketch_entity: dict) -> dict:
    """Extract the body's local (u, v, w) frame from the sketch entity.

    B-010 fix (2026-07-17): the previous implementation read
    `reference_plane.plane.{u_direction, v_direction}`, but those fields
    are None for the current history corpus (only `normal` and
    `transform.{x_axis, y_axis, z_axis}` are populated). The `transform`
    fields are the body's LOCAL 2D axes (u = transform.x_axis, v = transform.y_axis)
    and the extrude direction (w = transform.z_axis = plane normal).

    This fix gives the KQP dispatcher a frame that matches the body's
    actual orientation. Combined with the KQP frame-only mode, EX1/EX2
    perturbations (which swap plane/axes) are now detectable.
    """
    rp = sketch_entity.get("reference_plane", {})
    plane = rp.get("plane", {})
    transform = sketch_entity.get("transform", {}) or {}

    # Prefer the body's LOCAL frame (transform.x_axis = local u in 2D rect).
    # Fall back to reference_plane u_direction / v_direction if the
    # transform is missing (rare in the current corpus but defensive).
    u_t = vec_from_dict(transform.get("x_axis", {}))
    v_t = vec_from_dict(transform.get("y_axis", {}))
    z_t = vec_from_dict(transform.get("z_axis", {}))
    u_p = vec_from_dict(plane.get("u_direction", {}))
    v_p = vec_from_dict(plane.get("v_direction", {}))
    n_p = vec_from_dict(plane.get("normal", {}))

    # Use the transform's axes if all three are non-zero.  Otherwise
    # fall back to plane.{u_direction, v_direction, normal}.
    if any(c != 0 for c in u_t) and any(c != 0 for c in v_t):
        u = u_t
        v = v_t
    elif any(c != 0 for c in u_p) and any(c != 0 for c in v_p):
        u = u_p
        v = v_p
    else:
        u = (1.0, 0.0, 0.0)
        v = (0.0, 1.0, 0.0)
    # w = normal: prefer plane.normal, else transform.z_axis
    n = n_p if any(c != 0 for c in n_p) else z_t
    if not any(c != 0 for c in n):
        n = (0.0, 0.0, 1.0)

    u = tuple(clean_unit_vec_component(c) for c in u)
    v = tuple(clean_unit_vec_component(c) for c in v)
    n = tuple(clean_unit_vec_component(c) for c in n)
    u = normalize_vec3(*u)
    v = normalize_vec3(*v)
    w = normalize_vec3(*n)
    # recompute w = cross(u,v) to ensure orthogonality (defensive)
    w2 = normalize_vec3(*cross3(u, v))
    if all(abs(w[i]) < FLOAT_ZERO_TOL for i in range(3)) or abs(dot3(w, w2) - 1.0) > 0.01:
        w = w2
    return {"u_dir": list(u), "v_dir": list(v), "w_dir": list(w),
              "span_computation": "vertex_projection",
              "frame_source": "transform.x_axis+y_axis+plane.normal" if (
                  any(c != 0 for c in u_t) and any(c != 0 for c in v_t)
              ) else "plane.u_direction+v_direction+normal"}


# ---------------------------------------------------------------------------
# Stage 4: part_category + constraints
# ---------------------------------------------------------------------------

def classify_part_category(profiles: list[dict], extrude_distance_mm: float, dims: dict = None) -> str:
    """v0.6: quantified rules per part_category_rules in schema."""
    if not profiles:
        return "uncategorized"
    p0 = profiles[0]
    ptype = p0["type"]
    if ptype == "annulus":
        # bearing if thick, washer if thin
        if dims and "profiles" in dims:
            pd = dims["profiles"][0] if dims["profiles"] else {}
            orad = pd.get("outer_radius", {}).get("value", 0) if isinstance(pd, dict) else 0
            if orad and extrude_distance_mm > 0.3 * orad:
                return "bearing"
            return "washer"
        return "tube_or_sleeve"
    if ptype == "stadium":
        return "stadium_extrusion"
    if ptype == "polygon_with_fillets":
        return "bracket_with_fillets"
    if ptype == "rectangular_frame":
        return "frame_or_hollow_box"
    if ptype == "circle":
        if dims and "profiles" in dims:
            pd = dims["profiles"][0] if dims["profiles"] else {}
            r = pd.get("radius", {}).get("value", 0) if isinstance(pd, dict) else 0
            if r:
                return "disk" if extrude_distance_mm < 0.5 * r else "disk"
        return "disk"
    if ptype == "rectangle":
        # v0.6 quantified: need in-plane dims
        if dims and "profiles" in dims:
            pd = dims["profiles"][0] if dims["profiles"] else {}
            lu = pd.get("length_u", {}).get("value", 0) if isinstance(pd, dict) else 0
            wv = pd.get("width_v", {}).get("value", 0) if isinstance(pd, dict) else 0
            if lu and wv:
                in_plane = sorted([lu, wv])
                d_min, d_mid = in_plane[0], in_plane[1]
                d_max = max(lu, wv, extrude_distance_mm)
                d_min_all = min(lu, wv, extrude_distance_mm)
                aspect = d_max / d_min_all if d_min_all > 0 else 0
                if d_min == d_mid and aspect > 3:
                    return "square_strut"
                if aspect > 10 and d_min_all < d_mid * 0.3:
                    return "flat_plate_or_panel"
                if aspect > 10:
                    return "rectangular_slat_or_strip"
                if aspect < 1.5:
                    return "block"
                return "rectangular_prism_generic"
        return "block"
    return "uncategorized"


def extract_constraints(sketch_entity: dict, profile_classes: list[dict]) -> list:
    """Structured constraints from Fusion constraints."""
    cons = sketch_entity.get("constraints", {})
    points = sketch_entity.get("points", {})
    out = []
    counts: dict[str, int] = {}
    for c in cons.values():
        ctype = c.get("type")
        counts[ctype] = counts.get(ctype, 0) + 1
        if ctype in ("HorizontalConstraint", "VerticalConstraint"):
            continue  # captured by orthogonal_adjacent_edges
        if ctype == "ParallelConstraint":
            out.append({"type": "parallel", "curve_a": c.get("line_one"), "curve_b": c.get("line_two"), "tol": 1e-6})
        elif ctype == "PerpendicularConstraint":
            out.append({"type": "perpendicular", "curve_a": c.get("line_one"), "curve_b": c.get("line_two"), "tol": 1e-6})
        elif ctype == "TangentConstraint":
            out.append({"type": "tangent", "curve_a": c.get("curve_one"), "curve_b": c.get("curve_two"), "tol": 1e-6})
        elif ctype == "ConcentricConstraint":
            out.append({"type": "concentric", "circle_a": c.get("curve_one"), "circle_b": c.get("curve_two"), "tol": 1e-6})
        elif ctype == "CoincidentConstraint":
            # inert if the two referenced points are already at same coords
            e1 = c.get("entity")
            e2 = c.get("point")
            p1 = points.get(e1, {})
            p2 = points.get(e2, {})
            if p1 and p2:
                d = dist3(vec_from_dict(p1), vec_from_dict(p2))
                if d < FLOAT_ROUND_TOL:
                    out.append({"type": "coincident_inert", "note": "geometrically_inert", "tol": 1e-6})
                else:
                    out.append({"type": "coincident", "curve_a": e1, "curve_b": e2, "tol": 1e-6})
        elif ctype == "EqualConstraint":
            # v0.5 NEW: two curves equal (e.g. equal-radius holes)
            out.append({"type": "equal", "curve_a": c.get("curve_one"), "curve_b": c.get("curve_two"), "tol": 1e-6})
        elif ctype == "MidPointConstraint":
            out.append({"type": "midpoint", "point": c.get("point"), "curve": c.get("mid_point_curve"), "tol": 1e-6})

    # v0.5 NEW: implicit concentricity inference.
    # If 2+ circles' centers are all coincident (via CoincidentConstraints) to a
    # common point, infer concentricity between them. Handles sample 36 pattern
    # (2 CoincidentConstraints linking both circle centers to sketch origin).
    if not any(o["type"] == "concentric" for o in out):
        curves = sketch_entity.get("curves", {})
        circles = [(cid, c) for cid, c in curves.items() if c.get("type") == "SketchCircle"]
        if len(circles) >= 2:
            # build map: circle_id -> center_point_id
            circle_centers = {cid: c.get("center_point") for cid, c in circles}
            # find CoincidentConstraints linking a circle's center_point to another point
            coinc_links = {}  # point_id -> set of circle_ids
            for c in cons.values():
                if c.get("type") != "CoincidentConstraint":
                    continue
                # CoincidentConstraint links an 'entity' (often a sketch point) to a 'point'
                ent = c.get("entity")
                pt = c.get("point")
                # check if ent or pt is a circle center
                for cid, ctr in circle_centers.items():
                    if ctr in (ent, pt):
                        other = pt if ctr == ent else ent
                        coinc_links.setdefault(other, set()).add(cid)
            # if any single point links 2+ circles, they're concentric
            for pt, cids in coinc_links.items():
                if len(cids) >= 2:
                    cid_list = list(cids)
                    for i in range(len(cid_list)):
                        for j in range(i + 1, len(cid_list)):
                            out.append({"type": "concentric", "circle_a": cid_list[i],
                                        "circle_b": cid_list[j], "tol": 1e-6,
                                        "note": "inferred from shared CoincidentConstraint point"})
    return out, counts


# ---------------------------------------------------------------------------
# Stage 5: validation_intents
# ---------------------------------------------------------------------------

def build_validation_intents(body: dict, properties: dict) -> list:
    intents = []
    intents.append({"id": "q_body_count", "intent": "body_count", "expected": 1})
    # span_along_frame_axis for u, v, w
    spans = compute_spans(body)
    for axis, val in [("u", spans["u"]), ("v", spans["v"]), ("w", spans["w"])]:
        intents.append({"id": f"q_span_{axis}", "intent": "span_along_frame_axis",
                        "frame_axis": axis, "expected": round(val, 6), "tolerance": 0.01})
    # surface types from GT properties (Non-Leakage note: these are DERIVED expectations)
    surf = {}
    for st in properties.get("surface_types", []):
        surf[st["surface_type"]] = st["face_count"]
    if surf:
        intents.append({"id": "q_surf_dist", "intent": "surface_type_distribution", "expected": surf})
        cyl = surf.get("CylinderSurfaceType", 0)
        if cyl:
            intents.append({"id": "q_cyl_count", "intent": "cylinder_face_count", "expected": cyl})
    # through_void_count: count inner rings across all profiles
    void_count = sum(len([r for r in p["rings"] if r["role"] == "inner"]) for p in body["profiles"])
    if void_count:
        intents.append({"id": "q_void_count", "intent": "through_void_count", "expected": void_count})
    intents.append({"id": "q_is_solid", "intent": "is_solid", "expected": True})
    intents.append({"id": "q_occt_valid", "intent": "occt_is_valid", "expected": True})
    # edge_orthogonality only for planar profiles
    if all(p["type"] in ("rectangle", "rectangular_frame") for p in body["profiles"]):
        intents.append({"id": "q_edge_ortho", "intent": "edge_orthogonality", "subject": "body_0",
                        "expected": "3 direction groups", "tolerance": 1e-6})
    return intents


def compute_spans(body: dict) -> dict:
    """Approximate u/v/w spans from profile dimensions (best-effort, mm)."""
    # This is a simplified span estimate from dimensions; true spans need STEP geometry.
    p0 = body["profiles"][0]
    ptype = p0["type"]
    pdims = body["dimensions"]["profiles"][0] if body["dimensions"].get("profiles") else {}
    extrude = body["dimensions"]["extrude_distance"]["value"]
    if ptype == "rectangle":
        return {"u": pdims.get("length_u", {}).get("value", 0),
                "v": pdims.get("width_v", {}).get("value", 0), "w": extrude}
    if ptype == "circle":
        r = pdims.get("radius", {}).get("value", 0)
        return {"u": 2 * r, "v": 2 * r, "w": extrude}
    if ptype == "annulus":
        r = pdims.get("outer_radius", {}).get("value", 0)
        return {"u": 2 * r, "v": 2 * r, "w": extrude}
    if ptype == "stadium":
        sl = pdims.get("straight_length", {}).get("value", 0)
        r = pdims.get("radius", {}).get("value", 0)
        return {"u": sl + 2 * r, "v": 2 * r, "w": extrude}
    if ptype == "rectangular_frame":
        return {"u": pdims.get("outer_length_u", {}).get("value", 0),
                "v": pdims.get("outer_width_v", {}).get("value", 0), "w": extrude}
    return {"u": 0, "v": 0, "w": extrude}


# ---------------------------------------------------------------------------
# Stage 6: assemble + output
# ---------------------------------------------------------------------------

def compile_design_plan(json_path: Path) -> dict:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    md = data.get("metadata", {})
    properties = data.get("properties", {})
    warnings = []

    graph = build_dependency_graph(data)
    if len(graph["extrudes"]) != 1:
        warnings.append(f"Expected 1 extrude, found {len(graph['extrudes'])}; using first.")
    extrude_ent = graph["extrudes"][0]["entity"] if graph["extrudes"] else {}

    # collect input profiles
    input_profiles = extrude_ent.get("profiles", [])
    if not input_profiles:
        warnings.append("Extrude has no input profiles.")
        # fallback: use first sketch
        if graph["sketches"]:
            sketch_ent = graph["sketches"][0]["entity"]
            prof_ids = list(sketch_ent.get("profiles", {}).keys())[:1]
            input_profiles = [{"sketch": graph["sketches"][0]["id"], "profile": prof_ids[0]}] if prof_ids else []

    # group profiles by sketch (typically 1 sketch)
    sketch_id = input_profiles[0].get("sketch") if input_profiles else None
    sketch_ent = next((s["entity"] for s in graph["sketches"] if s["id"] == sketch_id), {})

    profile_classes = []
    for ip in input_profiles:
        pc = classify_profile(sketch_ent, ip.get("profile"))
        profile_classes.append(pc)

    frame = extract_frame(sketch_ent)
    extrude_block = extract_extrude(extrude_ent, properties)
    # v0.6: pass extrude_block so extract_dimensions can REUSE distance_total
    # (single source, eliminates dual-computation inconsistency risk).
    dims, dim_warnings = extract_dimensions(sketch_ent, profile_classes[0], extrude_ent, extrude_block)
    warnings.extend(dim_warnings)
    # v0.5: frame-aware direction cross-validation for one_side/degenerate_two_side.
    # If extrude direction_verified == "needs_frame_check", verify against GT bbox
    # projected onto w_dir.
    if extrude_block.get("direction_verified") == "needs_frame_check":
        w_dir = frame["w_dir"]
        bbox = properties.get("bounding_box", {})
        mn = bbox.get("min_point", {})
        mx = bbox.get("max_point", {})
        # project bbox corners onto w_dir; if span is entirely on negative side,
        # direction should be -w
        corners = []
        for sx in (mn.get("x",0), mx.get("x",0)):
            for sy in (mn.get("y",0), mx.get("y",0)):
                for sz in (mn.get("z",0), mx.get("z",0)):
                    corners.append(sx*w_dir[0]+sy*w_dir[1]+sz*w_dir[2])
        lo, hi = min(corners), max(corners)
        if hi < FLOAT_ROUND_TOL and lo < -FLOAT_ROUND_TOL:
            # body entirely on -w side -> direction should be -w
            if extrude_block["direction"] == "+w":
                extrude_block["direction"] = "-w"
                warnings.append("DIRECTION CORRECTED: source distance positive but GT bbox shows body in -w direction (sample 36 pattern). Cross-validation flipped +w -> -w.")
        extrude_block["direction_verified"] = True
    constraints, cons_counts = extract_constraints(sketch_ent, profile_classes)

    # primitive_type from primary profile
    prim_map = {"rectangle": "extruded_rectangle", "circle": "extruded_circle",
                "annulus": "extruded_annulus", "stadium": "extruded_stadium",
                "polygon_with_fillets": "extruded_polygon_with_fillets",
                "rectangular_frame": "extruded_rectangular_frame",
                "arbitrary_closed": "extruded_profile"}
    primitive_type = prim_map.get(profile_classes[0]["type"], "extruded_profile")

    body = {
        "id": "body_0",
        "primitive_type": primitive_type,
        "frame": frame,
        "profiles": profile_classes,
        "extrude": extrude_block,
        "dimensions": dims,
        "modifications": [],
    }

    # strip internal _curve_types before output
    for p in body["profiles"]:
        for r in p["rings"]:
            r.pop("_curve_types", None)

    part_category = classify_part_category(profile_classes, dims["extrude_distance"]["value"], dims)

    intents = build_validation_intents(body, properties)

    # auxiliary geometry
    aux = {"unused_sketches": len(graph["unused_sketch_ids"]),
           "note": "Unconsumed sketches present." if graph["unused_sketch_ids"] else "None."}

    plan = {
        "schema_version": "design_plan_v0.4",
        "sample_id": (json_path.parent.name if json_path.parent.name
                          else json_path.stem),
        "source_component_name": md.get("component_name", ""),
        "unit": "mm",
        "coordinate_system": {
            "frame": "part_local", "origin_convention": "bbox_min_corner",
            "axes": {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}, "unit": "mm",
        },
        "target": {
            "object_type": "single_part", "part_category": part_category,
            "body_count": 1, "engineering_description": "(compiler-generated; no NL description)",
        },
        "solid_bodies": [body],
        "auxiliary_geometry": aux,
        "constraints": constraints,
        "validation_intents": intents,
        "derived": {"part_category": part_category, "world_bbox_estimate": {"along_x": 0, "along_y": 0, "along_z": 0}},
        "non_verifiable": {"world_pose": "Assembly-context world coordinates omitted."},
        "compiler_notes": {
            "source_sketch_count": len(graph["sketches"]),
            "source_extrude_count": len(graph["extrudes"]),
            "explicit_dimension_count": sum(1 for d in sketch_ent.get("dimensions", {}).values() if d.get("is_driving")),
            "inferred_dimensions": [k for k, v in _flatten_sources(dims) if "inferred" in v],
            "inference_mode": _inference_mode(sketch_ent, dims),
            "source_constraints": [{"type": k, "count": v} for k, v in cons_counts.items()],
            "warnings": warnings,
            "unit_conversion_applied": "cm_to_mm (x10)",
        },
    }
    return plan


def _flatten_sources(dims: dict):
    """Yield (key, source) for all dimension entries with a source field."""
    for k, v in dims.items():
        if isinstance(v, dict) and "source" in v:
            yield k, v["source"]
        if k == "profiles":
            for pd in v:
                for pk, pv in pd.items():
                    if isinstance(pv, dict) and "source" in pv:
                        yield pk, pv["source"]
                    if isinstance(pv, list):
                        for item in pv:
                            if isinstance(item, dict) and "source" in item:
                                yield pk, item["source"]


def _inference_mode(sketch_entity: dict, dims: dict) -> str:
    """v0.6: classify how dimensions were sourced.

    none  = all in-plane dims have explicit_dimension source
    partial = some inferred_from_point_span / curve_field
    all   = ALL in-plane dims inferred (0 explicit driving dimensions in source)
    """
    explicit_count = sum(1 for d in sketch_entity.get("dimensions", {}).values() if d.get("is_driving"))
    if explicit_count == 0:
        # check if there are any in-plane dims at all (rect/circle have them)
        return "all"
    # count inferred sources among profile dims
    inferred = 0
    total = 0
    for pk, psrc in _flatten_sources(dims):
        if pk in ("extrude_distance",):
            continue
        total += 1
        if "inferred" in psrc or "curve_field" in psrc:
            inferred += 1
    if total == 0:
        return "none"
    if inferred == 0:
        return "none"
    if inferred == total:
        return "all"
    return "partial"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_plan_compiler.py <input.json> [output.json]")
        sys.exit(1)
    inp = Path(sys.argv[1])
    plan = compile_design_plan(inp)
    if len(sys.argv) >= 3:
        out = Path(sys.argv[2])
    else:
        out = inp.with_suffix(".design_plan.json")
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
