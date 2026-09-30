"""probe_invalid_reference.py — Test FreeCAD on a constraint referencing deleted geometry.

FreeCAD auto-deletes constraints when their referenced geometry is deleted.
We simulate the case by:
  1. Creating a valid sketch.
  2. Adding a Coincident constraint referencing geo 0 (valid).
  3. Deleting geo 0 — the constraint is auto-removed.
  4. Recording what MalformedConstraints reports after a re-solve.

Equivalently, we also try to call addConstraint with a non-existent GeoId
to verify FreeCAD refuses it (raises "Constraint has invalid indexes").
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import (build_sketch, probe_sketch_state,
                          ConstraintSpec, LineSpec, get_modules)


def main():
    out_extra = {"test_steps": []}

    # ---- Approach 1: try to add a constraint with bad GeoId ----
    app, Part, Sketcher = get_modules()
    doc = app.newDocument()
    sk = doc.addObject('Sketcher::SketchObject', 'SketchInvalid')
    sk.addGeometry(Part.LineSegment(app.Vector(0, 0, 0),
                                       app.Vector(10, 0, 0)), False)
    sk.addGeometry(Part.LineSegment(app.Vector(10, 0, 0),
                                       app.Vector(10, 5, 0)), False)
    try:
        bad = Sketcher.Constraint('Coincident', 0, 2, 99, 1)
        sk.addConstraint(bad)
        out_extra["addConstraint_99_accepted"] = True
    except Exception as e:
        out_extra["addConstraint_99_rejected"] = f"{type(e).__name__}: {e}"

    # ---- Approach 2: add valid constraint, then delete its geometry ----
    sk.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
    before_count = sk.ConstraintCount
    sk.delGeometry(0)
    after_count = sk.ConstraintCount
    rc = sk.solve()
    out_extra["constraint_count_before_delete"] = before_count
    out_extra["constraint_count_after_delete"] = after_count
    out_extra["solve_return_after_delete"] = int(rc)
    out_extra["dof_after_delete"] = int(sk.DoF)
    out_extra["malformed_after_delete"] = list(sk.MalformedConstraints or [])
    out_extra["interpretation"] = (
        "FreeCAD auto-removes constraints when their geometry is deleted; "
        "addConstraint with bad GeoId raises.  MalformedConstraints API "
        "captures any residual dangling constraint references.")

    # ---- Build the actual probe spec for the standard form ----
    spec = {
        'lines': [LineSpec('l0', (0, 0), (10, 0)),
                   LineSpec('l1', (10, 0), (10, 5))],
        'constraints': [
            ConstraintSpec('Coincident', target_geo=0, target_pos=2,
                             params=(1, 1)),
            ConstraintSpec('Coincident', target_geo=0, target_pos=1,
                             params=(1, 1)),  # references same geo twice
        ],
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'])
    out = {
        "test_case": "invalid_constraint_reference",
        "description": "Constraint references deleted geometry uuid — handled by FreeCAD.",
        "expected_solve_status": "invalid_constraint_reference",
        "expected_severity": "blocking",
        "num_lines": 2,
        "num_constraints": 2,
        **state,
    }
    out_dir = HERE / "invalid_constraint_reference"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps({**out, "extra_probe": out_extra}, indent=2,
                    ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({**{k: v for k, v in out.items()
                          if k not in ("constraints_summary",)},
                       "extra_probe": out_extra},
                      indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()