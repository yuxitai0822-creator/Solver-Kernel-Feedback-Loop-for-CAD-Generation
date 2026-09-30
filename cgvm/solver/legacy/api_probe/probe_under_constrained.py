"""probe_under_constrained.py — Test FreeCAD on an under-constrained rectangle.

A rotated rectangle with only 2 of 4 orientation constraints + no
distance / coincident constraints.  DoF should be > 0.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import (build_sketch, probe_sketch_state,
                          ConstraintSpec, LineSpec)


def rotated_rect_lines(theta_deg=30.0):
    theta = math.radians(theta_deg)
    cos, sin = math.cos(theta), math.sin(theta)

    def R(px, py):
        return (px * cos - py * sin, px * sin + py * cos)

    p0 = R(-5, -2.5)
    p1 = R(5, -2.5)
    p2 = R(5, 2.5)
    p3 = R(-5, 2.5)
    return [
        LineSpec('l0', p0, p1),
        LineSpec('l1', p1, p2),
        LineSpec('l2', p2, p3),
        LineSpec('l3', p3, p0),
    ]


def main():
    lines = rotated_rect_lines(theta_deg=30.0)
    spec = {
        'lines': lines,
        'constraints': [
            # Only 2 of 4 orientation constraints.
            ConstraintSpec('Horizontal', target_geo=0),
            ConstraintSpec('Vertical', target_geo=3),
            # No distance constraints, no coincident on corners.
        ],
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'])
    out = {
        "test_case": "under_constrained_rectangle",
        "description": "Rotated 30° rectangle with only 2 orientation constraints.",
        "expected_solve_status": "under_constrained",
        "expected_severity": "warning",
        "num_lines": 4,
        "num_constraints": 2,
        **state,
    }
    out_dir = HERE / "under_constrained_rectangle"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                       if k not in ("constraints_summary",)}, indent=2,
                       ensure_ascii=False))


if __name__ == "__main__":
    main()