"""test_pipeline.py — Run the unified Solver Feedback v0.1 pipeline on the 6
api_probe test cases and emit normalized outputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api_probe.probe_lib import (
    PointSpec, LineSpec, ConstraintSpec,
)
from core.pipeline import build_solver_feedback


def _make_history(points, lines, circles, constraints,
                    deleted_entities=None) -> dict:
    """Build a minimal history JSON for the pipeline."""
    ents = {}
    sketch_uuid = "sketch_test"
    ents[sketch_uuid] = {
        "type": "Sketch",
        "name": "Sketch1",
        "reference_plane": {"plane": {"origin": {"x": 0, "y": 0, "z": 0},
                                       "u_direction": {"x": 1, "y": 0, "z": 0},
                                       "v_direction": {"x": 0, "y": 1, "z": 0},
                                       "normal": {"x": 0, "y": 0, "z": 1}}},
        "points": {p.uuid: {"type": "Point3D", "x": p.x, "y": p.y, "z": 0.0}
                    for p in points.values()},
        "curves": {
            **{l.uuid: {
                "type": "SketchLine",
                "start_point": l.start_uuid,
                "end_point": l.end_uuid,
                "construction_geom": False,
                "fixed": False,
                "fully_constrained": False,
                "reference": False,
                "visible": True,
            } for l in lines.values()},
        },
        "constraints": {
            c.id: _constraint_to_f360(c) for c in constraints
        },
        "profiles": {"profile_test": {
            "loops": [{"is_outer": True,
                        "profile_curves": [{"curve": l.uuid, "type": "Line3D"}
                                            for l in lines.values()]}]
        }},
    }
    ents["extrude_test"] = {
        "type": "ExtrudeFeature",
        "profiles": [{"profile": "profile_test", "sketch": sketch_uuid}],
        "operation": "NewBodyFeatureOperation",
        "extent_type": "OneSideFeatureExtentType",
        "extent_one": {"distance": {"type": "ModelParameter", "value": 10.0},
                        "type": "DistanceExtentDefinition"},
        "extent_two": None,
    }
    history = {
        "metadata": {"parent_project": "test", "component_name": "test",
                       "component_index": 0},
        "timeline": [
            {"index": 1, "entity": sketch_uuid},
            {"index": 2, "entity": "extrude_test"},
        ],
        "entities": ents,
    }
    if deleted_entities:
        # Inject a "fake" dangling reference: a constraint whose entity
        # uuid does not appear in points/curves.
        for de in deleted_entities:
            if de not in ents[sketch_uuid]["points"] and de not in ents[sketch_uuid]["curves"]:
                # Add a stub point so the constraint is parseable
                ents[sketch_uuid]["points"][de] = {"type": "Point3D",
                                                    "x": 0, "y": 0, "z": 0}
                # But mark it deleted by giving it a "_deleted" flag (custom).
                # The history_parser will still see it; the invalid_constraint
                # will be caught when the adapter can't find the referenced
                # entity in the parsed constraints dict.  Easier: just
                # delete it from entities.
                del ents[sketch_uuid]["points"][de]
    return history


def _constraint_to_f360(c: ConstraintSpec) -> dict:
    """Convert our spec back to a Fusion360-style constraints entry."""
    if c.type == "Horizontal":
        return {"type": "HorizontalConstraint", "line": c.entities[0]}
    if c.type == "Vertical":
        return {"type": "VerticalConstraint", "line": c.entities[0]}
    if c.type == "Coincident":
        return {"type": "CoincidentConstraint",
                "entity": c.entities[0], "point": c.entities[1]}
    if c.type == "Offset":
        # c.entities is [point_a, point_b, axis?]
        ent = {"type": "OffsetConstraint",
               "entity_one": c.entities[0], "entity_two": c.entities[1],
               "distance": {"value": c.value}}
        if len(c.entities) > 2:
            ent["axis_hint"] = c.entities[2]  # non-standard, used by parser
        return ent
    return {"type": c.type}


def case_under_constrained():
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
        "p2": PointSpec("p2", 10, 5),
        "p3": PointSpec("p3", 0, 5),
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
        "l1": LineSpec("l1", "p1", "p2"),
        "l2": LineSpec("l2", "p2", "p3"),
        "l3": LineSpec("l3", "p3", "p0"),
    }
    constraints = [
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
    ]
    return _make_history(points, lines, {}, constraints)


def case_fully_constrained():
    """Rectangle: 4 orientations + length constraints along x AND y."""
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
        "p2": PointSpec("p2", 10, 5),
        "p3": PointSpec("p3", 0, 5),
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
        "l1": LineSpec("l1", "p1", "p2"),
        "l2": LineSpec("l2", "p2", "p3"),
        "l3": LineSpec("l3", "p3", "p0"),
    }
    constraints = [
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
        ConstraintSpec("c_v0", "Vertical", ["l1"]),
        ConstraintSpec("c_v1", "Vertical", ["l3"]),
        # length l0 = 10 along x
        ConstraintSpec("c_dx_l0", "Offset", ["p0", "p1", "x"], 10.0),
        # length l1 = 5 along y
        ConstraintSpec("c_dy_l1", "Offset", ["p1", "p2", "y"], 5.0),
    ]
    return _make_history(points, lines, {}, constraints)


def case_redundant():
    """Fully-constrained rectangle + 1 extra Horizontal(l0) duplicate."""
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
        "p2": PointSpec("p2", 10, 5),
        "p3": PointSpec("p3", 0, 5),
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
        "l1": LineSpec("l1", "p1", "p2"),
        "l2": LineSpec("l2", "p2", "p3"),
        "l3": LineSpec("l3", "p3", "p0"),
    }
    constraints = [
        ConstraintSpec("c_h0a", "Horizontal", ["l0"]),
        ConstraintSpec("c_h0b", "Horizontal", ["l0"]),  # REDUNDANT
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
        ConstraintSpec("c_v0", "Vertical", ["l1"]),
        ConstraintSpec("c_v1", "Vertical", ["l3"]),
        ConstraintSpec("c_dx_l0", "Offset", ["p0", "p1", "x"], 10.0),
        ConstraintSpec("c_dy_l1", "Offset", ["p1", "p2", "y"], 5.0),
    ]
    return _make_history(points, lines, {}, constraints)


def case_conflicting():
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
    }
    lines = {"l0": LineSpec("l0", "p0", "p1")}
    constraints = [
        ConstraintSpec("c_h", "Horizontal", ["l0"]),
        ConstraintSpec("c_v", "Vertical", ["l0"]),
    ]
    return _make_history(points, lines, {}, constraints)


def case_invalid_reference():
    """Constraint references a deleted line uuid."""
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
        "p2": PointSpec("p2", 10, 5),
        "p3": PointSpec("p3", 0, 5),
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
        "l1": LineSpec("l1", "p1", "p2"),
        "l2": LineSpec("l2", "p2", "p3"),
        "l3": LineSpec("l3", "p3", "p0"),
    }
    constraints = [
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l_deleted"]),  # references deleted line
    ]
    history = _make_history(points, lines, {}, constraints,
                              deleted_entities={"l_deleted"})
    return history


def case_recompute_failure():
    """Sketch OK but extrude distance = 0."""
    points = {
        "p0": PointSpec("p0", 0, 0),
        "p1": PointSpec("p1", 10, 0),
        "p2": PointSpec("p2", 10, 5),
        "p3": PointSpec("p3", 0, 5),
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
        "l1": LineSpec("l1", "p1", "p2"),
        "l2": LineSpec("l2", "p2", "p3"),
        "l3": LineSpec("l3", "p3", "p0"),
    }
    constraints = [
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
        ConstraintSpec("c_v0", "Vertical", ["l1"]),
        ConstraintSpec("c_v1", "Vertical", ["l3"]),
    ]
    history = _make_history(points, lines, {}, constraints)
    # Force extrude.distance = 0
    history["entities"]["extrude_test"]["extent_one"]["distance"]["value"] = 0.0
    return history


CASES = [
    ("under_constrained_rectangle", case_under_constrained),
    ("fully_constrained_rectangle", case_fully_constrained),
    ("redundant_rectangle", case_redundant),
    ("conflicting_line_orientation", case_conflicting),
    ("invalid_constraint_reference", case_invalid_reference),
    ("recompute_failure_case", case_recompute_failure),
]


def main():
    out_root = Path(__file__).resolve().parent / "outputs"
    out_root.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, builder in CASES:
        print(f"\n=== {name} ===")
        try:
            history = builder()
            fb = build_solver_feedback(history, sample_id=name,
                                         sketch_id="Sketch1")
            (out_root / f"{name}.solver_feedback.json").write_text(
                json.dumps(fb, indent=2, ensure_ascii=False),
                encoding="utf-8")
            print(f"  status={fb['solve']['solve_status']} severity={fb['solve']['severity']} "
                  f"dof={fb['solve']['dof']} recompute={fb['recompute']['recompute_status']}")
            print(f"  blocking={len(fb['llm_feedback']['blocking_errors'])} "
                  f"warnings={len(fb['llm_feedback']['warnings'])}")
            summary.append({
                "case": name,
                "solve_status": fb['solve']['solve_status'],
                "severity": fb['solve']['severity'],
                "dof": fb['solve']['dof'],
                "recompute_status": fb['recompute']['recompute_status'],
                "n_blocking": len(fb['llm_feedback']['blocking_errors']),
                "n_warnings": len(fb['llm_feedback']['warnings']),
            })
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            import traceback; traceback.print_exc()
            summary.append({"case": name, "error": str(e)})
    (out_root / "_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()