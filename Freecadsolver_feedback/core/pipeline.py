"""pipeline.py — Unified Solver Feedback v0.1 (FreeCAD backend) pipeline.

Same 4-layer architecture as Kiwisolver_feedback:
  L1 raw          ← solver_runner.run_solver_from_history
  L2 normalized   ← diagnostic_normalizer.normalize_solve + .normalize_recompute
  L3 diagnostics  ← diagnostics_builder.build_constraint_diagnostics
                    (no-op fallback for FreeCAD)
  L4 llm_feedback ← feedback_builder.build_llm_feedback
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.solver_runner import run_solver_from_history
from core.recompute_runner import run_recompute_from_state
from core.registry_builder import build_registry_from_state
from core.diagnostic_normalizer import normalize_solve, normalize_recompute
from core.fallback_analyzer import run_fallbacks
from core.diagnostics_builder import build_constraint_diagnostics
from core.feedback_builder import build_llm_feedback


def build_solver_feedback(history: dict,
                            sample_id: str = "unknown",
                            sketch_id: str = "Sketch1",
                            script_executed: bool = True,
                            execution_error: str | None = None,
                            run_fallback: bool = True) -> dict:
    """Full V0.1 pipeline.  Returns schema-valid solver feedback JSON."""
    # L1
    raw = run_solver_from_history(history)
    rc = run_recompute_from_state(raw)
    reg = build_registry_from_state(raw)

    # L3 (FreeCAD doesn't need fallback)
    fallback: dict[str, Any] = {"used": False, "method": None,
                                  "redundant_constraint_ids": [],
                                  "suspected_conflicting_constraint_ids": []}
    if run_fallback:
        try:
            fallback = run_fallbacks(history, raw)
        except Exception as e:
            fallback = {"used": True, "method": "FAILED",
                          "note": f"{type(e).__name__}: {e}",
                          "redundant_constraint_ids": [],
                          "suspected_conflicting_constraint_ids": []}

    deleted = set(raw.get("deleted_entities_referenced", []))
    diagnostics = build_constraint_diagnostics(raw, fallback, deleted)

    # L2
    normalized = normalize_solve(raw)
    # Augment L2 with the full redundant/conflicting/malformed lists from raw.
    normalized["redundant_constraint_ids"] = raw.get("redundant_constraints", [])
    normalized["conflicting_constraint_ids"] = raw.get("conflicting_constraints", [])
    normalized["malformed_constraint_ids"] = raw.get("malformed_constraints", [])
    normalized_rc = normalize_recompute(rc)

    # L4
    llm_feedback = build_llm_feedback(normalized, diagnostics, fallback,
                                         normalized_rc)

    out = {
        "solver_feedback_version": "v0.1",
        "sample_id": sample_id,
        "sketch_id": sketch_id,
        "runtime": {
            "script_executed": script_executed,
            "execution_error": execution_error,
        },
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
            "used": fallback.get("used", False),
            "method": fallback.get("method"),
            "redundant_constraint_ids": fallback.get("redundant_constraint_ids", []),
            "suspected_conflicting_constraint_ids":
                fallback.get("suspected_conflicting_constraint_ids", []),
            "note": fallback.get("note"),
        },
        "llm_feedback": llm_feedback,
    }
    return out


def write_solver_feedback(history: dict, out_path: str | Path,
                            sample_id: str = "unknown",
                            sketch_id: str = "Sketch1",
                            script_executed: bool = True,
                            execution_error: str | None = None,
                            run_fallback: bool = True) -> dict:
    """Build + write to file."""
    fb = build_solver_feedback(history, sample_id=sample_id,
                                 sketch_id=sketch_id,
                                 script_executed=script_executed,
                                 execution_error=execution_error,
                                 run_fallback=run_fallback)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(fb, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    return fb