"""probe_fully_constrained.py — Test FreeCAD on a fully-constrained rectangle.

We start with a non-axis-aligned rectangle (rotated 30°) so that the
orientation constraints (Horizontal/Vertical) actually do work, then add
4 corner-coincidences and DistanceX/Y.  DoF should be 0.
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


def rotated_rect(center=(0, 0), w=10, h=5, theta_deg=30.0):
    """Build a rotated-rectangle line spec."""
    theta = math.radians(theta_deg)
    cos, sin = math.cos(theta), math.sin(theta)
    cx, cy = center

    def R(px, py):
        x = px * cos - py * sin + cx
        y = px * sin + py * cos + cy
        return (x, y)

    p0 = R(-w / 2, -h / 2)
    p1 = R(w / 2, -h / 2)
    p2 = R(w / 2, h / 2)
    p3 = R(-w / 2, h / 2)
    return [
        LineSpec('l0', p0, p1),
        LineSpec('l1', p1, p2),
        LineSpec('l2', p2, p3),
        LineSpec('l3', p3, p0),
    ]


def main():
    lines = rotated_rect(theta_deg=30.0)
    spec = {
        'lines': lines,
        'constraints': [
            ConstraintSpec('Horizontal', target_geo=0),
            ConstraintSpec('Vertical', target_geo=1),
            ConstraintSpec('Horizontal', target_geo=2),
            ConstraintSpec('Vertical', target_geo=3),
            ConstraintSpec('Coincident', target_geo=0, target_pos=2, params=(1, 1)),
            ConstraintSpec('Coincident', target_geo=1, target_pos=2, params=(2, 1)),
            ConstraintSpec('Coincident', target_geo=2, target_pos=2, params=(3, 1)),
            ConstraintSpec('Coincident', target_geo=3, target_pos=2, params=(0, 1)),
            ConstraintSpec('DistanceX', target_geo=0, target_pos=2, params=(10.0,)),
            ConstraintSpec('DistanceY', target_geo=1, target_pos=2, params=(5.0,)),
        ],
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'])
    out = {
        "test_case": "fully_constrained_rectangle",
        "description": "Rotated 30° rectangle with 4 orientations + 4 corner-coincidences + 2 distance constraints.",
        "expected_solve_status": "fully_constrained",
        "expected_severity": "pass",
        "num_lines": 4,
        "num_constraints": 10,
        **state,
    }
    out_dir = HERE / "fully_constrained_rectangle"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                       if k not in ("constraints_summary",)}, indent=2,
                       ensure_ascii=False))


if __name__ == "__main__":
    main()