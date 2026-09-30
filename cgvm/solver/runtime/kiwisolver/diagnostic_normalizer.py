"""diagnostic_normalizer.py — Convert raw solver result to Layer 2 normalized state.

Maps raw_solver_output (from solver_runner) into:
    {
      'solve_status': 'fully_constrained' | 'under_constrained' | 'over_constrained'
                     | 'conflicting' | 'redundant' | 'unsolvable'
                     | 'invalid_constraint_reference' | 'unknown',
      'severity':     'pass' | 'warning' | 'blocking' | 'error',
      'dof':          int | None,
      'flags': {
        'has_conflict':           bool,
        'has_redundancy':         bool,
        'has_invalid_constraints': bool,
      },
      'recompute_status': 'success' | 'failed' | 'skipped' | 'unknown'
    }
"""
from __future__ import annotations

from typing import Any


def normalize_solve(raw: dict, redundancy_count: int = 0) -> dict:
    """raw: from solver_runner.run_solver_from_history
    redundancy_count: filled in later by fallback_analyzer.
    """
    raw_solve = raw.get("raw_solve", {})
    invalid = raw.get("invalid_constraint_ids", [])
    semantic = raw.get("semantic_conflicts", [])
    dof = raw.get("dof_estimate")
    non_linear = raw.get("non_linear_constraints", [])

    rc = raw_solve.get("return_code", 0)
    exc = raw_solve.get("exception", None)

    has_conflict = (rc != 0) or bool(semantic)
    has_invalid = bool(invalid)
    has_redundancy = redundancy_count > 0

    # Determine solve_status.
    if has_invalid:
        solve_status = "invalid_constraint_reference"
        severity = "blocking"
    elif has_conflict:
        solve_status = "conflicting"
        severity = "blocking"
    elif has_redundancy and dof is not None and dof == 0:
        solve_status = "redundant"
        severity = "warning"
    elif dof is None:
        solve_status = "unknown"
        severity = "error"
    elif dof == 0:
        solve_status = "fully_constrained"
        severity = "pass"
    elif dof < 0:
        solve_status = "over_constrained"
        severity = "warning"
    else:
        solve_status = "under_constrained"
        severity = "warning"

    return {
        "solve_status": solve_status,
        "severity": severity,
        "dof": dof,
        "return_code": rc,
        "exception": exc,
        "message": raw_solve.get("message", ""),
        "flags": {
            "has_conflict": has_conflict,
            "has_redundancy": has_redundancy,
            "has_invalid_constraints": has_invalid,
            "has_non_linear_constraints": bool(non_linear),
        },
        "non_linear_constraint_ids": non_linear,
    }


def normalize_recompute(recompute_result: dict) -> dict:
    """recompute_result: from recompute_runner.run_recompute"""
    status = recompute_result.get("status", "unknown")
    return {
        "recompute_status": status,
        "failed_features": recompute_result.get("failed_features", []),
        "message": recompute_result.get("message"),
    }