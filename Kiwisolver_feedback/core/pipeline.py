"""pipeline.py — Unified Solver Feedback v0.1 pipeline.

Takes a Fusion360 history JSON and produces the full v0.1 schema-valid
solver feedback JSON.

Layers:
  L1 raw          ← solver_runner.run_solver_from_history
  L2 normalized   ← diagnostic_normalizer.normalize_solve + .normalize_recompute
  L3 diagnostics  ← diagnostics_builder.build_constraint_diagnostics
                    + fallback_analyzer.run_fallbacks
  L4 llm_feedback ← feedback_builder.build_llm_feedback
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.solver_runner import run_solver_from_history
from core.recompute_runner import run_recompute
from core.registry_builder import build_registry
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
    # Layer 1 — raw
    raw = run_solver_from_history(history)
    rc = run_recompute(history)
    reg = build_registry(history)

    # Layer 3 (in two parts: structural diagnostics + fallback)
    fallback: dict[str, Any] = {
        "used": False, "method": None,
        "redundant_constraint_ids": [],
        "suspected_conflicting_constraint_ids": [],
    }
    if run_fallback:
        try:
            fallback = run_fallbacks(history, raw)
        except Exception as e:
            fallback = {
                "used": True,
                "method": "leave-one-out-FAILED",
                "note": f"fallback_analyzer raised {type(e).__name__}: {e}",
                "redundant_constraint_ids": [],
                "suspected_conflicting_constraint_ids": [],
            }

    diagnostics = build_constraint_diagnostics(
        raw, fallback, raw.get("deleted_entities_referenced", []))

    # Layer 2 — normalized
    normalized = normalize_solve(
        raw, redundancy_count=len(fallback.get("redundant_constraint_ids", [])))
    normalized_rc = normalize_recompute(rc)

    # Layer 4 — LLM-facing feedback
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
    """Build + write to file.  Returns the dict."""
    fb = build_solver_feedback(history, sample_id=sample_id, sketch_id=sketch_id,
                                 script_executed=script_executed,
                                 execution_error=execution_error,
                                 run_fallback=run_fallback)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(fb, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    return fb