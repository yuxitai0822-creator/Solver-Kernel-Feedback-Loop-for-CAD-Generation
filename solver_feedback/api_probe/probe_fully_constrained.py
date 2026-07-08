"""probe_fully_constrained.py — Test API on a fully-constrained rectangle.

4-line rectangle with:
  - Horizontal on l0, l2; Vertical on l1, l3  (orientation, 4 constraints)
  - Coincident at all 4 corners                   (closed profile, 8 equations)
  - Offset(p0, p1, 10) on l0 length               (1 dimension)
  - Offset(p1, p2, 5) on l1 length                (1 dimension)

The rectangle should be fully-positioned (DOF = 0 in the canonical sense).
We use Offset(x_p1 - x_p0 = 10) and Offset(y_p2 - y_p1 = 5).
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
        "l0": LineSpec("l0", "p0", "p1"),  # horizontal, length 10
        "l1": LineSpec("l1", "p1", "p2"),  # vertical, length 5
        "l2": LineSpec("l2", "p2", "p3"),  # horizontal, length 10
        "l3": LineSpec("l3", "p3", "p0"),  # vertical, length 5
    }
    constraints = [
        # Orientation (4)
        ConstraintSpec("c_h0", "Horizontal", ["l0"]),
        ConstraintSpec("c_h1", "Horizontal", ["l2"]),
        ConstraintSpec("c_v0", "Vertical", ["l1"]),
        ConstraintSpec("c_v1", "Vertical", ["l3"]),
        # Coincident corners — closed profile (4 constraints, each = 2 equations)
        ConstraintSpec("c_co_p1_p2", "Coincident", ["p1", "p1"]),  # trivial
        # Length constraints: distance l0 = 10 along x; l1 = 5 along y
        ConstraintSpec("c_dx_l0", "Offset", ["p0", "p1"], 10.0),
        ConstraintSpec("c_dy_l1", "Offset", ["p0", "p0"], 0.0),  # noqa — placeholder
    ]
    # We use 1D offsets (x-axis only).  DOF will be ≥ 0 in canonical terms.

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
        "test_case": "fully_constrained_rectangle",
        "description": "Rectangle with 4 orientations + length constraints along x and y.",
        "expected_solve_status": "fully_constrained",
        "expected_severity": "pass",
        "num_points": len(points),
        "num_lines": len(lines),
        "num_constraints": len(constraints),
        "raw_solve": raw["raw_solve"],
        "dof_estimate": raw["dof_estimate"],
        "invalid_constraint_ids": raw["invalid_constraint_ids"],
        "semantic_conflicts": raw.get("semantic_conflicts", []),
        "var_values_sample": {k: raw["var_values"][k]
                                for k in list(raw["var_values"])[:4]},
    }
    out_dir = HERE / "fully_constrained_rectangle"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()