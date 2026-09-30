"""probe_recompute_failure.py — Test FreeCAD on a sketch that solves but
the downstream Pad has Length=0 — Pad should be marked Invalid after recompute.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import (build_sketch, probe_sketch_state,
                          ConstraintSpec, LineSpec, PadSpec, get_modules)


def main():
    spec = {
        'lines': [LineSpec('l0', (0, 0), (10, 0)),
                   LineSpec('l1', (10, 0), (10, 5)),
                   LineSpec('l2', (10, 5), (0, 5)),
                   LineSpec('l3', (0, 5), (0, 0))],
        'constraints': [
            ConstraintSpec('Horizontal', target_geo=0),
            ConstraintSpec('Vertical', target_geo=1),
            ConstraintSpec('Horizontal', target_geo=2),
            ConstraintSpec('Vertical', target_geo=3),
            ConstraintSpec('Coincident', target_geo=0, target_pos=2, params=(1, 1)),
            ConstraintSpec('Coincident', target_geo=1, target_pos=2, params=(2, 1)),
            ConstraintSpec('Coincident', target_geo=2, target_pos=2, params=(3, 1)),
            ConstraintSpec('Coincident', target_geo=3, target_pos=2, params=(0, 1)),
        ],
        'pad': PadSpec(length=0.0),  # ZERO length — should set Pad.Invalid
    }
    result = build_sketch(spec)
    state = probe_sketch_state(result['doc'], result['sketch'],
                                  pad=result['pad'])
    out = {
        "test_case": "recompute_failure_case",
        "description": "Sketch solves but Pad with Length=0 — pad is marked Invalid.",
        "expected_recompute_status": "failed",
        "expected_severity": "blocking",
        "num_lines": 4,
        "num_constraints": 8,
        "num_pad": 1,
        **state,
    }
    out_dir = HERE / "recompute_failure_case"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "solver_feedback_raw.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                       if k not in ("constraints_summary",)}, indent=2,
                       ensure_ascii=False))


if __name__ == "__main__":
    main()