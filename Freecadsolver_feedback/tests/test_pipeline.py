"""test_pipeline.py — Run the unified Solver Feedback v0.1 (FreeCAD) pipeline
on the 6 spec test cases and emit schema-valid outputs.

This is the FreeCAD counterpart of Kiwisolver_feedback/tests/test_pipeline.py.
Each test case is built directly in FreeCAD (no Fusion360 history needed);
the output is the same v0.1 schema-valid JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api_probe"))

from api_probe.probe_lib import (build_sketch, probe_sketch_state,
                                  LineSpec, ConstraintSpec, PadSpec)
from core.diagnostic_normalizer import normalize_solve, normalize_recompute
from core.registry_builder import build_registry_from_state
from core.recompute_runner import run_recompute_from_state
from core.fallback_analyzer import run_fallbacks
from core.diagnostics_builder import build_constraint_diagnostics
from core.feedback_builder import build_llm_feedback


def rotated_rect_lines(theta_deg=30.0):
    import math
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


def run_pipeline_through_sketch(name: str, dc_spec: dict) -> dict:
    """Run the unified 4-layer pipeline on a FreeCAD sketch built from dc_spec."""
    # 1. Build sketch in FreeCAD
    result = build_sketch(dc_spec)
    state = probe_sketch_state(result['doc'], result['sketch'],
                                  pad=result.get('pad'))

    # 2. Layer 1 → Layer 2
    normalized = normalize_solve(state)
    normalized["redundant_constraint_ids"] = state.get("redundant_constraints", [])
    normalized["conflicting_constraint_ids"] = state.get("conflicting_constraints", [])
    normalized["malformed_constraint_ids"] = state.get("malformed_constraints", [])

    # 3. Recompute
    rc = run_recompute_from_state(state)
    normalized_rc = normalize_recompute(rc)

    # 4. Registry
    reg = build_registry_from_state(state)

    # 5. Diagnostics (no fallback for FreeCAD)
    fallback = run_fallbacks({}, state)
    deleted = set(state.get("deleted_entities_referenced", []))
    diagnostics = build_constraint_diagnostics(state, fallback, deleted)

    # 6. LLM feedback
    llm_feedback = build_llm_feedback(normalized, diagnostics, fallback,
                                         normalized_rc)

    out = {
        "solver_feedback_version": "v0.1",
        "sample_id": name,
        "sketch_id": "Sketch1",
        "runtime": {"script_executed": True, "execution_error": None},
        "solve": normalized,
        "recompute": normalized_rc,
        "registry": {
            "num_geometries": reg["num_geometries"],
            "num_constraints": reg["num_constraints"],
            "geometry_registry": reg["geometry_registry"],
            "constraint_registry": reg["constraint_registry"],
        },
        "constraint_diagnostics": diagnostics,
        "fallback_diagnostics": {
            "used": False,
            "method": None,
            "redundant_constraint_ids": [],
            "suspected_conflicting_constraint_ids": [],
            "note": "FreeCAD Sketcher exposes redundant/conflicting constraints directly; no fallback needed.",
        },
        "llm_feedback": llm_feedback,
    }
    return out


# ---------------------------------------------------------------------------
# 6 spec test cases
# ---------------------------------------------------------------------------

def case_under_constrained():
    return run_pipeline_through_sketch("under_constrained_rectangle", {
        "lines": rotated_rect_lines(),
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),
            ConstraintSpec("Vertical", target_geo=3),
        ],
    })


def case_fully_constrained():
    return run_pipeline_through_sketch("fully_constrained_rectangle", {
        "lines": rotated_rect_lines(),
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),
            ConstraintSpec("Vertical", target_geo=1),
            ConstraintSpec("Horizontal", target_geo=2),
            ConstraintSpec("Vertical", target_geo=3),
            ConstraintSpec("Coincident", target_geo=0, target_pos=2, params=(1, 1)),
            ConstraintSpec("Coincident", target_geo=1, target_pos=2, params=(2, 1)),
            ConstraintSpec("Coincident", target_geo=2, target_pos=2, params=(3, 1)),
            ConstraintSpec("Coincident", target_geo=3, target_pos=2, params=(0, 1)),
            ConstraintSpec("DistanceX", target_geo=0, target_pos=2, params=(10.0,)),
            ConstraintSpec("DistanceY", target_geo=1, target_pos=2, params=(5.0,)),
        ],
    })


def case_redundant():
    return run_pipeline_through_sketch("redundant_rectangle", {
        "lines": rotated_rect_lines(),
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),  # c0
            ConstraintSpec("Horizontal", target_geo=0),  # c1 = REDUNDANT
            ConstraintSpec("Vertical", target_geo=1),
            ConstraintSpec("Horizontal", target_geo=2),
            ConstraintSpec("Vertical", target_geo=3),
        ],
    })


def case_conflicting():
    return run_pipeline_through_sketch("conflicting_line_orientation", {
        "lines": [LineSpec("l0", (0, 0), (10, 0))],
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),
            ConstraintSpec("Vertical", target_geo=0),
        ],
    })


def case_invalid_reference():
    """Simulate by adding a Coincident that references the same line twice
    (a constraint configuration the solver cannot satisfy)."""
    return run_pipeline_through_sketch("invalid_constraint_reference", {
        "lines": rotated_rect_lines(),
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),
            ConstraintSpec("Vertical", target_geo=1),
            ConstraintSpec("Horizontal", target_geo=2),
            ConstraintSpec("Vertical", target_geo=3),
            # Conflicting geometry reference: coincident with itself
            ConstraintSpec("Coincident", target_geo=0, target_pos=1, params=(0, 1)),
        ],
    })


def case_recompute_failure():
    return run_pipeline_through_sketch("recompute_failure_case", {
        "lines": [
            LineSpec("l0", (0, 0), (10, 0)),
            LineSpec("l1", (10, 0), (10, 5)),
            LineSpec("l2", (10, 5), (0, 5)),
            LineSpec("l3", (0, 5), (0, 0)),
        ],
        "constraints": [
            ConstraintSpec("Horizontal", target_geo=0),
            ConstraintSpec("Vertical", target_geo=1),
            ConstraintSpec("Horizontal", target_geo=2),
            ConstraintSpec("Vertical", target_geo=3),
            ConstraintSpec("Coincident", target_geo=0, target_pos=2, params=(1, 1)),
            ConstraintSpec("Coincident", target_geo=1, target_pos=2, params=(2, 1)),
            ConstraintSpec("Coincident", target_geo=2, target_pos=2, params=(3, 1)),
            ConstraintSpec("Coincident", target_geo=3, target_pos=2, params=(0, 1)),
        ],
        "pad": PadSpec(length=0.0),  # ZERO length → Pad.Invalid
    })


CASES = [
    ("under_constrained_rectangle", case_under_constrained),
    ("fully_constrained_rectangle", case_fully_constrained),
    ("redundant_rectangle", case_redundant),
    ("conflicting_line_orientation", case_conflicting),
    ("invalid_constraint_reference", case_invalid_reference),
    ("recompute_failure_case", case_recompute_failure),
]


def main():
    out_root = Path(__file__).resolve().parent / "outputs"
    out_root.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, builder in CASES:
        print(f"\n=== {name} ===")
        try:
            fb = builder()
            (out_root / f"{name}.solver_feedback.json").write_text(
                json.dumps(fb, indent=2, ensure_ascii=False),
                encoding="utf-8")
            print(f"  status={fb['solve']['solve_status']} "
                  f"severity={fb['solve']['severity']} "
                  f"dof={fb['solve']['dof']} "
                  f"recompute={fb['recompute']['recompute_status']}")
            print(f"  blocking={len(fb['llm_feedback']['blocking_errors'])} "
                  f"warnings={len(fb['llm_feedback']['warnings'])}")
            print(f"  llm summary: {fb['llm_feedback']['summary'][:120]}")
            summary.append({
                "case": name,
                "solve_status": fb["solve"]["solve_status"],
                "severity": fb["solve"]["severity"],
                "dof": fb["solve"]["dof"],
                "recompute_status": fb["recompute"]["recompute_status"],
                "n_blocking": len(fb["llm_feedback"]["blocking_errors"]),
                "n_warnings": len(fb["llm_feedback"]["warnings"]),
            })
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            import traceback; traceback.print_exc()
            summary.append({"case": name, "error": str(e)})
    (out_root / "_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()