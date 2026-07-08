"""history_parser.py — Translate Fusion360 history JSON → solver-feedback specs.

Input:  history JSON (the same model consumed by ReconstructionEngine v0.1)
Output: (points, lines, circles, constraints, deleted_entities) — the
        abstract spec consumed by `solver_runner.run_solver()`.

History schema (Fusion360 Gallery reconstruction):
    entities[UUID] = Sketch | ExtrudeFeature | ...
    Sketch:     points, curves, constraints
                constraints[i] = {
                    'type': 'Coincident' | 'Horizontal' | 'Vertical' | ...
                    'entity_one' / 'line' / etc.: uuid or shape
                    'value' / 'distance' (for Offset / Dimension)
                }
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_history(history: dict) -> tuple[dict, dict, dict, list, set]:
    """Extract solver-feedback specs from a history JSON.

    Returns: (points, lines, circles, constraints, deleted_entities)
        points: { uuid: {'x': float, 'y': float} }
        lines:  { uuid: {'start': uuid, 'end': uuid, 'construction': bool} }
        circles: {}   (sketch circles live in curves[*], not top-level)
        constraints: list of dicts with keys {id, type, entities, value}
        deleted_entities: set of uuid referenced by a constraint but missing
                          from the sketch (this is itself a fault signal).
    """
    entities = history.get("entities", {})
    sketch_uuid = None
    sketch = None
    for ev in history.get("timeline", []):
        e = entities.get(ev.get("entity", ""), {})
        if e.get("type") == "Sketch" and sketch is None:
            sketch = e
            sketch_uuid = ev.get("entity")
            break
    if sketch is None:
        return {}, {}, {}, [], set()

    # 1. Points
    points: dict[str, dict] = {}
    for pid, p in sketch.get("points", {}).items():
        points[pid] = {
            "x": float(p.get("x", 0.0)),
            "y": float(p.get("y", 0.0)),
        }

    # 2. Lines (only SketchLine)
    lines: dict[str, dict] = {}
    for cid, c in sketch.get("curves", {}).items():
        if c.get("type") != "SketchLine":
            continue
        sp = c.get("start_point")
        ep = c.get("end_point")
        if not sp or not ep:
            continue
        lines[cid] = {
            "start": sp,
            "end": ep,
            "construction": bool(c.get("construction_geom", False)),
        }

    # 3. Circles (kept for compatibility; V0.1 doesn't translate circle radius
    # constraints directly into kiwisolver)
    circles: dict[str, dict] = {}

    # 4. Constraints
    constraints: list[dict] = []
    referenced: set[str] = set()
    for cid, c in sketch.get("constraints", {}).items():
        ct = c.get("type", "")
        spec = _translate_constraint(cid, ct, c)
        if spec is None:
            continue
        constraints.append(spec)
        # 'entities' may include an axis hint ('x' / 'y') for Offset — skip those
        # when collecting entity-references for deletion detection.
        for ent in spec.get("entities", []):
            if ent in ("x", "y"):
                continue
            referenced.add(ent)

    # 5. Detect dangling references → deleted_entities
    deleted: set[str] = set()
    for ent in referenced:
        if ent not in points and ent not in lines and ent not in circles:
            deleted.add(ent)

    return points, lines, circles, constraints, deleted


def _translate_constraint(constraint_id: str, ctype: str,
                            c: dict) -> dict | None:
    """Map a Fusion360 constraint entry to solver-feedback spec.

    Returns None if the constraint type is not supported in V0.1.
    """
    spec = {"id": constraint_id, "type": ctype, "entities": [], "value": None}

    # Map known constraint types.
    if ctype == "CoincidentConstraint":
        spec["type"] = "Coincident"
        e = c.get("entity")
        p = c.get("point")
        if e and p:
            # entity may be a curve — we ignore vertex-on-curve cases in V0.1.
            return None
        # V0.1 only handles point-point coincident
        return None  # Most coincidents in Fusion360 are point-on-curve

    if ctype == "HorizontalConstraint":
        spec["type"] = "Horizontal"
        spec["entities"] = [c.get("line")] if c.get("line") else []
        return spec if spec["entities"] else None

    if ctype == "VerticalConstraint":
        spec["type"] = "Vertical"
        spec["entities"] = [c.get("line")] if c.get("line") else []
        return spec if spec["entities"] else None

    if ctype == "PerpendicularConstraint":
        spec["type"] = "Perpendicular"
        spec["entities"] = [c.get("line_one"), c.get("line_two")]
        return spec if all(spec["entities"]) else None

    if ctype == "ParallelConstraint":
        spec["type"] = "Parallel"
        spec["entities"] = [c.get("line_one"), c.get("line_two")]
        return spec if all(spec["entities"]) else None

    if ctype == "TangentConstraint":
        spec["type"] = "Tangent"
        spec["entities"] = [c.get("curve_one"), c.get("curve_two")]
        return spec if all(spec["entities"]) else None

    if ctype == "ConcentricConstraint":
        spec["type"] = "Concentric"
        spec["entities"] = [c.get("curve_one"), c.get("curve_two")]
        return spec if all(spec["entities"]) else None

    if ctype == "EqualConstraint":
        spec["type"] = "Equal"
        spec["entities"] = list(c.get("curves") or [])
        return spec if len(spec["entities"]) >= 2 else None

    if ctype == "MidPointConstraint":
        spec["type"] = "MidPoint"
        spec["entities"] = [c.get("point"), c.get("mid_point_curve")]
        return spec if all(spec["entities"]) else None

    if ctype == "OffsetConstraint":
        spec["type"] = "Offset"
        spec["entities"] = [c.get("entity_one"), c.get("entity_two")]
        spec["value"] = c.get("distance", {}).get("value") \
            if isinstance(c.get("distance"), dict) else c.get("distance")
        # Optional axis hint (non-standard, set by V0.1 test pipeline).
        axis_hint = c.get("axis_hint")
        if axis_hint in ("x", "y"):
            spec["entities"].append(axis_hint)
        return spec if all(spec["entities"]) and spec["value"] is not None else None

    # Dimensions are not direct kiwisolver constraints but are useful for
    # V0.2 extension; V0.1 returns None.
    return None


def load_history_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))