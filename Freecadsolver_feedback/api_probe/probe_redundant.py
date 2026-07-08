"""probe_redundant.py — Test FreeCAD on a rotated rectangle with a redundant
duplicate constraint.

A rotated 30° rectangle with 4 orientations + 1 extra Horizontal(l0)
duplicate — FreeCAD should report the duplicate in RedundantConstraints
and solve() returns -2.
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
            ConstraintSpec('Horizontal', target_geo=0),  # c0
            ConstraintSpec('Horizontal', target_geo=0),  # c1 = REDUNDANT duplicate
            ConstraintSpec('Vertical', target_geo=1),
            ConstraintSpec('Horizontal', target_geo=2),
            ConstraintSpec('Vertical', target_geo=3),
        ],
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'])
    out = {
        "test_case": "redundant_rectangle",
        "description": "Rotated 30° rectangle with 4 orientations + 1 duplicate Horizontal(l0).",
        "expected_solve_status": "redundant",
        "expected_severity": "warning",
        "num_lines": 4,
        "num_constraints": 5,
        **state,
    }
    out_dir = HERE / "redundant_rectangle"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                       if k not in ("constraints_summary",)}, indent=2,
                       ensure_ascii=False))


if __name__ == "__main__":
    main()