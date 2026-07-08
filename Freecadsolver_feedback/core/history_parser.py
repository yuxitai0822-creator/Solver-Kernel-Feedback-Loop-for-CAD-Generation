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

    # 1. Lines: only SketchLine → LineSegment
    line_uuid_to_geo_id: dict[str, int] = {}
    lines_spec: list[dict] = []
    for cid, c in sketch.get("curves", {}).items():
        if c.get("type") != "SketchLine":
            continue
        sp = c.get("start_point")
        ep = c.get("end_point")
        if not sp or not ep:
            continue
        sp_p = sketch.get("points", {}).get(sp, {})
        ep_p = sketch.get("points", {}).get(ep, {})
        s_xy = (float(sp_p.get("x", 0)), float(sp_p.get("y", 0)))
        e_xy = (float(ep_p.get("x", 0)), float(ep_p.get("y", 0)))
        line_uuid_to_geo_id[cid] = len(lines_spec)
        lines_spec.append({"uuid": cid, "start": s_xy, "end": e_xy})

    # 2. Constraints
    constraints_spec: list[dict] = []
    non_linear: list[str] = []
    deleted: set[str] = set()

    for cid, c in sketch.get("constraints", {}).items():
        ctype = c.get("type", "")
        if ctype == "HorizontalConstraint":
            gid = line_uuid_to_geo_id.get(c.get("line"))
            if gid is None:
                deleted.add(c.get("line", ""))
                continue
            constraints_spec.append({"type": "Horizontal", "target_geo": gid,
                                        "target_pos": -1, "params": (),
                                        "f360_id": cid})
        elif ctype == "VerticalConstraint":
            gid = line_uuid_to_geo_id.get(c.get("line"))
            if gid is None:
                deleted.add(c.get("line", ""))
                continue
            constraints_spec.append({"type": "Vertical", "target_geo": gid,
                                        "target_pos": -1, "params": (),
                                        "f360_id": cid})
        elif ctype == "CoincidentConstraint":
            a, b = c.get("entity"), c.get("point")
            # For V0.1: treat as point-point coincident (vertex-on-vertex).
            # The point uuid maps to the line endpoint in our sketch spec.
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
        "constraints": constraints_spec,
        "non_linear": non_linear,
        "deleted_entities": deleted,
        "pad": pad_spec,
    }