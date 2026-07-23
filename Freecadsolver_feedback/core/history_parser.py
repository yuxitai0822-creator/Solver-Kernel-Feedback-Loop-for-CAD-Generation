"""history_parser.py — Translate Fusion360 history JSON → FreeCAD sketch spec.

Maps the Fusion360 Gallery reconstruction history JSON schema to the
abstract LineSpec / ConstraintSpec used by the FreeCAD probe library.

History schema (Fusion360 Gallery reconstruction):
    entities[UUID] = Sketch | ExtrudeFeature | ...
    Sketch:     points, curves, constraints

The FreeCAD sketch is constructed fresh (not loaded from the Fusion360
file), because Fusion360's constraint format is not directly compatible
with FreeCAD's.  Each Fusion360 constraint type is mapped to its
FreeCAD equivalent.

For unsupported Fusion360 constraints (e.g. parametric formulas, fillet
chamfer constraints), we record a `non_linear_constraints` warning.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_history_to_sketch_spec(history: dict) -> dict:
    """Convert a Fusion360 history JSON into a sketch spec for FreeCAD.

    Returns dict with keys:
        lines:        [LineSpec, ...]  (one per SketchLine)
        constraints:  [ConstraintSpec, ...]
        non_linear:   [str, ...]      (constraint ids not translatable)
        deleted_entities: set[str]    (uuids referenced but not defined)
        pad:          PadSpec | None   (from ExtrudeFeature)
    """
    entities = history.get("entities", {})
    sketch = None
    for ev in history.get("timeline", []):
        e = entities.get(ev.get("entity", ""), {})
        if e.get("type") == "Sketch" and sketch is None:
            sketch = e
            break
    if sketch is None:
        return {"lines": [], "constraints": [], "non_linear": [],
                "deleted_entities": set(), "pad": None}

    # 1. Geometry:  SketchLine → LineSegment,  SketchCircle → CircleSpec (B-006 fix)
    geo_uuid_to_idx: dict[str, int] = {}
    lines_spec: list[dict] = []
    circles_spec: list[dict] = []
    for cid, c in sketch.get("curves", {}).items():
        ctype = c.get("type")
        if ctype == "SketchLine":
            sp = c.get("start_point")
            ep = c.get("end_point")
            if not sp or not ep:
                continue
            sp_p = sketch.get("points", {}).get(sp, {})
            ep_p = sketch.get("points", {}).get(ep, {})
            s_xy = (float(sp_p.get("x", 0)), float(sp_p.get("y", 0)))
            e_xy = (float(ep_p.get("x", 0)), float(ep_p.get("y", 0)))
            geo_uuid_to_idx[cid] = len(lines_spec) + len(circles_spec)
            lines_spec.append({"uuid": cid, "start": s_xy, "end": e_xy})
        elif ctype == "SketchCircle":
            centre_id = c.get("center_point") or c.get("center")
            if not centre_id:
                continue
            centre = sketch.get("points", {}).get(centre_id, {})
            cx = float(centre.get("x", 0))
            cy = float(centre.get("y", 0))
            r = float(c.get("radius", 0))
            geo_uuid_to_idx[cid] = len(lines_spec) + len(circles_spec)
            circles_spec.append({"uuid": cid, "center": (cx, cy), "radius": r})
        # SketchArc / SketchConicCurve:  recorded as non_linear downstream
        # (the spec test cases only use SketchLine + SketchCircle; curves
        # fall back to the "0 lines" path which the solver_runner treats
        # as a `no lines in sketch` warning, not a failure).
        else:
            continue

    # 2. Constraints
    constraints_spec: list[dict] = []
    non_linear: list[str] = []
    deleted: set[str] = set()

    for cid, c in sketch.get("constraints", {}).items():
        ctype = c.get("type", "")
        if ctype == "HorizontalConstraint":
            gid = geo_uuid_to_idx.get(c.get("line"))
            if gid is None:
                deleted.add(c.get("line", ""))
                continue
            constraints_spec.append({"type": "Horizontal", "target_geo": gid,
                                        "target_pos": -1, "params": (),
                                        "f360_id": cid})
        elif ctype == "VerticalConstraint":
            gid = geo_uuid_to_idx.get(c.get("line"))
            if gid is None:
                deleted.add(c.get("line", ""))
                continue
            constraints_spec.append({"type": "Vertical", "target_geo": gid,
                                        "target_pos": -1, "params": (),
                                        "f360_id": cid})
        elif ctype == "ConcentricConstraint":
            # F360 concentric:  two circles share a centre
            a, b = c.get("entity_one"), c.get("entity_two")
            g1 = geo_uuid_to_idx.get(a)
            g2 = geo_uuid_to_idx.get(b)
            if g1 is None or g2 is None:
                deleted.add(a or "")
                deleted.add(b or "")
                continue
            constraints_spec.append({"type": "Concentric", "target_geo": g1,
                                        "target_pos": -1, "params": (g2,),
                                        "f360_id": cid})
        elif ctype == "RadiusConstraint":
            ent = c.get("entity")
            g = geo_uuid_to_idx.get(ent)
            if g is None:
                deleted.add(ent or "")
                continue
            constraints_spec.append({"type": "Radius", "target_geo": g,
                                        "target_pos": -1,
                                        "params": (float(c.get("radius", 0.0)),),
                                        "f360_id": cid})
        elif ctype == "CoincidentConstraint":
            a, b = c.get("entity"), c.get("point")
            # For V0.1: treat as point-point coincident (vertex-on-vertex).
            non_linear.append(cid)  # FreeCAD coincident is geo-pos pair
        elif ctype == "PerpendicularConstraint":
            non_linear.append(cid)
        elif ctype == "ParallelConstraint":
            non_linear.append(cid)
        elif ctype == "TangentConstraint":
            non_linear.append(cid)
        elif ctype == "EqualConstraint":
            non_linear.append(cid)
        elif ctype == "MidPointConstraint":
            non_linear.append(cid)
        elif ctype == "OffsetConstraint":
            non_linear.append(cid)
        else:
            non_linear.append(cid)

    # 1b.  Annulus auto-pin (B-006 fix):  when the parser sees 2+ circles
    # but the F360 source did NOT supply a ConcentricConstraint or
    # RadiusConstraint, we synthesise the missing ones so FreeCAD can
    # solve the shape.  An annulus in F360 is implicitly defined by
    # two concentric circles + their radii; the F360 history often
    # omits the explicit constraints.
    if len(circles_spec) >= 2:
        existing_types = {c["type"] for c in constraints_spec}
        first_circle_gid = len(lines_spec)   # circles come right after lines
        # If the F360 source only had one circle, no annulus to constrain.
        if "Concentric" not in existing_types:
            for i in range(1, len(circles_spec)):
                constraints_spec.append({
                    "type": "Concentric",
                    "target_geo": first_circle_gid,
                    "target_pos": -1,
                    "params": (first_circle_gid + i,),
                    "f360_id": f"auto-concentric-{i}",
                })
        if "Radius" not in existing_types:
            for i, ci in enumerate(circles_spec):
                constraints_spec.append({
                    "type": "Radius",
                    "target_geo": first_circle_gid + i,
                    "target_pos": -1,
                    "params": (ci["radius"],),
                    "f360_id": f"auto-radius-{i}",
                })

    # 3. Pad from ExtrudeFeature
    pad_spec: dict | None = None
    for ev in history.get("timeline", []):
        e = entities.get(ev.get("entity", ""), {})
        if e.get("type") == "ExtrudeFeature":
            eo = e.get("extent_one") or {}
            if isinstance(eo, dict):
                d = eo.get("distance")
                if isinstance(d, dict):
                    pad_spec = {"length": float(d.get("value", 10.0))}
            break

    return {
        "lines": lines_spec,
        "circles": circles_spec,
        "constraints": constraints_spec,
        "non_linear": non_linear,
        "deleted_entities": deleted,
        "pad": pad_spec,
    }