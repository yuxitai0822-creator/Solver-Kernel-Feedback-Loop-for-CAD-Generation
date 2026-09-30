"""diagnostic_normalizer.py — Convert FreeCAD raw state → Layer 2 normalized state.

FreeCAD provides direct solver state (solve return code, DoF, conflict
/ redundant / malformed lists).  We map these into the same Layer 2
schema used by Kiwisolver_feedback for cross-backend compatibility.

FreeCAD solve() return codes:
  0   success
  -1  solver error
  -2  redundant
  -3  conflicting
  -4  over-constrained
  -5  malformed
"""
from __future__ import annotations

from typing import Any


def normalize_solve(raw: dict) -> dict:
    """Layer 1 raw → Layer 2 normalized.

    Args:
        raw: from solver_runner.run_solver_from_history
            (FreeCAD sketcher state dict)
    """
    rc = raw.get("solve_return_code", -1)
    dof = raw.get("dof", 0)
    redundant = raw.get("redundant_constraints", [])
    conflicting = raw.get("conflicting_constraints", [])
    malformed = raw.get("malformed_constraints", [])
    partially_redundant = raw.get("partially_redundant_constraints", [])
    missing_v_h = raw.get("missing_vertical_horizontal_constraints", [])
    non_linear = raw.get("non_linear_constraint_ids", [])
    raw_msg = raw.get("raw_solve", {}).get("message", "")

    has_conflict = bool(conflicting) or rc == -3
    has_redundancy = bool(redundant) or rc == -2
    has_invalid = bool(malformed) or rc == -5
    has_over_constrained = rc == -4
    has_partially_redundant = bool(partially_redundant)
    has_missing_vh = bool(missing_v_h)
    has_solver_error = rc == -1

    # Determine solve_status (single primary status; secondary signals in flags).
    if has_invalid:
        solve_status = "invalid_constraint_reference"
        severity = "blocking"
    elif has_conflict:
        solve_status = "conflicting"
        severity = "blocking"
    elif has_solver_error:
        # Could be conflicting (line collapsed) or other solver error;
        # without explicit Conflicting list we report 'conflicting' because
        # solve returned non-zero.
        solve_status = "conflicting"
        severity = "blocking"
    elif has_over_constrained:
        solve_status = "over_constrained"
        severity = "warning"
    elif has_redundancy:
        solve_status = "redundant"
        severity = "warning"
    elif dof == 0 and not has_missing_vh:
        solve_status = "fully_constrained"
        severity = "pass"
    elif dof > 0:
        solve_status = "under_constrained"
        severity = "warning"
    else:
        solve_status = "unknown"
        severity = "error"

    return {
        "solve_status": solve_status,
        "severity": severity,
        "dof": dof,
        "return_code": rc,
        "exception": raw.get("raw_solve", {}).get("exception"),
        "message": raw_msg or f"FreeCAD solve() returned {rc}",
        "flags": {
            "has_conflict": has_conflict,
            "has_redundancy": has_redundancy,
            "has_invalid_constraints": has_invalid,
            "has_over_constrained": has_over_constrained,
            "has_partially_redundant": has_partially_redundant,
            "has_missing_v_h_constraints": has_missing_vh,
            "has_non_linear_constraints": bool(non_linear),
            "has_solver_error": has_solver_error,
        },
        "non_linear_constraint_ids": non_linear,
        "redundant_constraint_ids": redundant,
        "conflicting_constraint_ids": conflicting,
        "malformed_constraint_ids": malformed,
    }


def normalize_recompute(recompute_result: dict) -> dict:
    """recompute_result: from recompute_runner.run_recompute_from_state"""
    return {
        "recompute_status": recompute_result.get("status", "unknown"),
        "failed_features": recompute_result.get("failed_features", []),
        "message": recompute_result.get("message"),
    }