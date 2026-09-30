"""probe_invalid_reference.py — Test API when a constraint references a deleted entity.

We declare points p0 and p1, but one constraint tries to Coincident p0 with
p_deleted which is not registered.  kiwisolver doesn't know about it; our
adapter must reject the constraint as invalid BEFORE adding to the solver.
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
    }
    lines = {
        "l0": LineSpec("l0", "p0", "p1"),
    }
    # Constraint c_coin tries to Coincident(p0, p_deleted); p_deleted is
    # not in the points dict.  Adapter should reject it as invalid.
    constraints = [
        ConstraintSpec("c_h", "Horizontal", ["l0"]),
        ConstraintSpec("c_coin_bad", "Coincident", ["p0", "p_deleted"]),
    ]

    solver, var, invalid = build_kiwi_system(points, lines, {}, constraints,
                                              deleted_entities={"p_deleted"})
    raw = probe_solve_system(solver, var, invalid, constraints,
                              deleted_entities={"p_deleted"},
                              degeneracy_check={
                                  "non_degenerate_line_lengths": {
                                      "l0": ("p0", "p1"),
                                  }
                              })

    out = {
        "test_case": "invalid_constraint_reference",
        "description": "Coincident constraint references a deleted geometry id (p_deleted).",
        "expected_solve_status": "invalid_constraint_reference",
        "expected_severity": "blocking",
        "num_constraints": len(constraints),
        "raw_solve": raw["raw_solve"],
        "dof_estimate": raw["dof_estimate"],
        "invalid_constraint_ids": raw["invalid_constraint_ids"],
        "semantic_conflicts": raw.get("semantic_conflicts", []),
        "deleted_entities_referenced": raw["deleted_entities_referenced"],
    }
    out_dir = HERE / "invalid_constraint_reference"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()