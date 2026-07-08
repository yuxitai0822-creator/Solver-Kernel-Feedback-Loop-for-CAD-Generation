"""probe_under_constrained.py — Test API on an under-constrained rectangle.

A 4-line rectangle where only Horizontal constraints are applied to
opposite sides — no Vertical, no Coincident at corners, no dimensions.
Result: the rectangle can scale in any direction; under-constrained.
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
    # Only horizontal constraints — no vertical, no coincident corners.
    constraints = [
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
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

    out = {
        "test_case": "under_constrained_rectangle",
        "description": "Rectangle with only horizontal constraints — should be under-constrained.",
        "expected_solve_status": "under_constrained",
        "expected_severity": "warning",
        "num_points": len(points),
        "num_lines": len(lines),
        "num_constraints": len(constraints),
        "raw_solve": raw["raw_solve"],
        "dof_estimate": raw["dof_estimate"],
        "invalid_constraint_ids": raw["invalid_constraint_ids"],
        "semantic_conflicts": raw.get("semantic_conflicts", []),
        "var_values_sample": {k: raw["var_values"][k] for k in list(raw["var_values"])[:4]},
    }
    out_dir = HERE / "under_constrained_rectangle"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()