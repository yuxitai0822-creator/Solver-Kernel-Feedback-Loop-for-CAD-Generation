"""probe_conflicting.py — Test FreeCAD on a line with conflicting orientations.

Same line constrained Horizontal AND Vertical — should report in
ConflictingConstraints and solve() returns -3.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import (build_sketch, probe_sketch_state,
                          ConstraintSpec, LineSpec)


def main():
    spec = {
        'lines': [LineSpec('l0', (0, 0), (10, 0))],
        'constraints': [
            ConstraintSpec('Horizontal', target_geo=0),
            ConstraintSpec('Vertical', target_geo=0),
        ],
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'])
    out = {
        "test_case": "conflicting_line_orientation",
        "description": "Line l0 constrained both Horizontal AND Vertical — should be conflicting.",
        "expected_solve_status": "conflicting",
        "expected_severity": "blocking",
        "num_lines": 1,
        "num_constraints": 2,
        **state,
    }
    out_dir = HERE / "conflicting_line_orientation"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                       if k not in ("constraints_summary",)}, indent=2,
                       ensure_ascii=False))


if __name__ == "__main__":
    main()