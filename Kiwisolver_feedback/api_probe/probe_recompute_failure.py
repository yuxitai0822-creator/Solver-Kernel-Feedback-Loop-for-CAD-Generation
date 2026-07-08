"""probe_recompute_failure.py — Test API on a sketch that solves but downstream
operation fails (recompute failure).

Sketch is fully valid; but the dependent Pad/Extrude has zero distance — the
operation should fail at recompute time, not at solver time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import (
    build_kiwi_system, probe_solve_system,
    PointSpec, LineSpec, ConstraintSpec,
)


def main():
    # Sketch solves cleanly.
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
    solver, var, invalid = build_kiwi_system(points, lines, {}, constraints,
                                              deleted_entities=set())
    raw = probe_solve_system(solver, var, invalid, constraints, set(),
                              degeneracy_check={
                                  "non_degenerate_line_lengths": {
                                      "l0": ("p0", "p1"),
                                      "l1": ("p1", "p2"),
                                      "l2": ("p2", "p3"),
                                      "l3": ("p3", "p0"),
                                  }
                              })

    # Simulate recompute: sketch solver pass, but downstream extrude feature
    # fails because extrude distance is 0.
    extrude_distance = 0.0  # the bug
    recompute_ok = extrude_distance > 0.0

    out = {
        "test_case": "recompute_failure_case",
        "description": "Sketch solves but downstream extrude feature fails (distance=0).",
        "expected_recompute_status": "failed",
        "expected_severity": "blocking",
        "sketch_solve_pass": True,
        "recompute_success": recompute_ok,
        "failed_features": [
            {"name": "ExtrudeFeature", "reason": "extrude.distance <= 0"}
        ],
        "raw_solve": raw["raw_solve"],
        "dof_estimate": raw["dof_estimate"],
        "invalid_constraint_ids": raw["invalid_constraint_ids"],
        "semantic_conflicts": raw.get("semantic_conflicts", []),
        "method": raw["method"],
    }
    out_dir = HERE / "recompute_failure_case"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()