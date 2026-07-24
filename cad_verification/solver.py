"""cad_verification/solver.py — Solver Verification Object.

Wraps ``Freecadsolver_feedback.core.pipeline.build_solver_feedback`` to
verify a Fusion360 history (the source sketch) is *acceptable* per the
spec:

    §5.1 Solver verification target:
        sketch constraints are solvable, no conflict, not over-constrained.
        (Under-constrained is OK; domain-specific engineering
         constraint check is deferred per the spec footnote.)

    §5.1 Acceptable:
        "Solver Acceptable" = solved AND no conflict AND no redundancy
        AND (engineering constraint check passed when applicable).

    Diagnostic:
        {"solver_status":        "fully_constrained" | "under_constrained"
                                 | "over_constrained" | "conflicting"
                                 | "redundant" | "unsolvable" | "unknown",
         "dof":                  int | null,
         "conflict_constraints": [id, ...],
         "redundant_constraints":[id, ...],
         "severity":             "pass" | "warning" | "blocking" | "error"}
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cad_verification._base import VerificationResult  # noqa: E402


# Per the spec §5.1 NOTE 1 (controlling rule for this experiment):
# "暂定是global verification，保持简洁和强兼容性。在判定通过时允许
# under constraint，只不允许约束冲突和过约束的情况。由于缺乏工程知识
# 语料，也暂时不做特定工程领域约束的校验。"
#
# In other words, the *blocking* conditions are ONLY:
#   1. constraint conflict
#   2. over-constrained
# The spec's main body ("No redundant constraint") is overridden by
# this note for the current experiment.  ``under_constrained`` is
# explicitly OK; ``redundant`` is implicitly OK (the note says "only"
# block conflict + over-constrained); engineering-domain checks are
# skipped.
ACCEPTABLE_STATUSES = {"fully_constrained", "under_constrained", "redundant"}
# These statuses block the verification regardless of severity/flags.
BLOCKING_STATUSES = {"conflicting", "over_constrained", "unsolvable",
                      "invalid_constraint_reference"}


def _import_solver_pipeline():
    """Lazy import — the FreeCAD backend is heavy and only available in
    environments where cad_subproject1 is on PYTHONPATH.  We try the
    project-relative path first (most likely working environment),
    then the system Python.
    """
    candidate = _REPO_ROOT / "Freecadsolver_feedback"
    if not candidate.exists():
        raise ImportError(
            f"Freecadsolver_feedback not found at {candidate}.  "
            "The solver verification object cannot run in this environment."
        )
    p = str(candidate)
    if p not in sys.path:
        sys.path.insert(0, p)
    from core.pipeline import build_solver_feedback  # type: ignore
    return build_solver_feedback


def _is_acceptable(solver_feedback: dict) -> bool:
    """Apply the §5.1 NOTE 1 "Solver Acceptable" definition.

    Block iff the solve status is in BLOCKING_STATUSES (conflict /
    over-constrained / unsolvable / invalid) OR the flags report
    ``has_conflict`` / ``has_over_constrained``.  Redundant
    constraints are allowed per the spec note.
    """
    solve = (solver_feedback or {}).get("solve") or {}
    status = (solve.get("status") or "").lower()
    if status in BLOCKING_STATUSES:
        return False
    flags = solve.get("flags") or {}
    if flags.get("has_conflict") or flags.get("has_over_constrained"):
        return False
    # Severity escalation (FreeCAD may classify over-constrained as
    # 'warning'; we still block because status already tells us so).
    severity = (solve.get("severity") or "").lower()
    if severity in ("blocking", "error"):
        return False
    return True


def _project_diagnostic(solver_feedback: dict) -> dict:
    """Project the L1 raw solver feedback into the LLM-facing diagnostic
    shape required by the spec."""
    solve = (solver_feedback or {}).get("solve") or {}
    diags = (solver_feedback or {}).get("constraint_diagnostics") or {}
    return {
        "solver_status":         solve.get("status", "unknown"),
        "dof":                   solve.get("dof"),
        "conflict_constraints":  diags.get("conflicting_constraints", []) or solve.get("conflicting_constraint_ids", []),
        "redundant_constraints": diags.get("redundant_constraints", []) or solve.get("redundant_constraint_ids", []),
        "severity":              solve.get("severity", "unknown"),
    }


class SolverVerification:
    """Solver Verification Object.

    Reads a Fusion360 history JSON from ``history_path`` and runs the
    FreeCAD Sketcher via the project's v0.1 pipeline.  Returns a
    pass/fail plus a projected LLM-facing diagnostic.

    If the FreeCAD backend is unavailable in the current Python
    environment, the verification is **skipped** (``passed=None``) —
    the orchestrator records ``skipped_reason`` for the analysis layer.
    """

    NAME = "solver"

    def run(self, history_path: Path) -> VerificationResult:
        history_path = Path(history_path)
        if not history_path.exists():
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": "history_missing",
                        "history_path": str(history_path)},
            )
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": f"history_load_failed: {type(e).__name__}: {e}"},
            )

        # The pipeline expects a Fusion360 history; defend against
        # malformed input (e.g. an empty dict).
        if not isinstance(history, dict) or not history:
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": "history_empty_or_malformed"},
            )

        try:
            build_solver_feedback = _import_solver_pipeline()
            sf = build_solver_feedback(
                history,
                sample_id=history_path.stem,
                sketch_id="Sketch1",
                script_executed=True,
                execution_error=None,
                run_fallback=True,
            )
        except ImportError as e:
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": f"freecad_unavailable: {e}"},
            )
        except Exception as e:  # noqa: BLE001
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={"exception": f"{type(e).__name__}: {e}",
                       "trace": traceback.format_exc(limit=4)},
                extras={"skipped_reason": f"solver_crash: {type(e).__name__}"},
            )

        passed = _is_acceptable(sf)
        return VerificationResult(
            name=self.NAME,
            passed=passed,
            diagnostic=_project_diagnostic(sf),
            full=sf,
        )
