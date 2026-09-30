"""probe_conflicting.py — Test API on a line that is both horizontal AND vertical.

Same line, two orientation constraints: Horizontal (y_s == y_e) AND Vertical
(x_s == x_e).  Only solvable if the line is a degenerate zero-length point,
which conflicts with the implicit non-degeneracy assumption.
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
        "p1": PointSpec("p1", 10, 0),  # horizontal line
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
    }
    # Conflict: l0 is constrained BOTH horizontal AND vertical — collapses
    # the line to a zero-length point, which conflicts with the user's intent.
    constraints = [
        ConstraintSpec("c_h", "Horizontal", ["l0"]),
        ConstraintSpec("c_v", "Vertical", ["l0"]),
    ]

    solver, var, invalid = build_kiwi_system(points, lines, {}, constraints,
                                              deleted_entities=set())
    raw = probe_solve_system(solver, var, invalid, constraints, set(),
                              degeneracy_check={
                                  "non_degenerate_line_lengths": {
                                      "l0": ("p0", "p1"),
                                  }
                              })

    out = {
        "test_case": "conflicting_line_orientation",
        "description": "Line l0 constrained both Horizontal AND Vertical — collapse to zero-length point.",
        "expected_solve_status": "conflicting",
        "expected_severity": "blocking",
        "num_constraints": len(constraints),
        "raw_solve": raw["raw_solve"],
        "dof_estimate": raw["dof_estimate"],
        "invalid_constraint_ids": raw["invalid_constraint_ids"],
        "semantic_conflicts": raw.get("semantic_conflicts", []),
        "method": raw["method"],
    }
    out_dir = HERE / "conflicting_line_orientation"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()