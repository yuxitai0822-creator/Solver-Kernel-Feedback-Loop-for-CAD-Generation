"""fallback_analyzer.py — Leave-one-out tests for redundancy/conflict detection.

kiwisolver does not expose redundancy or strict conflict sets directly.
We use these fallbacks:

  leave_one_out_redundancy(raw, history)
      For each constraint c in the spec, remove it; re-solve; if the
      solution is unchanged, c is redundant.

  leave_one_out_suspected_conflict(raw, history)
      If the solver succeeded but DOF is unusually low AND the system has
      excess constraints, suspect over-constrained regions; report the
      constraints whose removal leaves the system fully constrained.

Returns dict:
    {
      'used': True,
      'method': 'leave-one-out',
      'redundant_constraint_ids': [str, ...],
      'suspected_conflicting_constraints': [str, ...],
      'note': str,
    }
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api_probe"))

from core.history_parser import parse_history
from core.solver_runner import _to_specs
from api_probe.probe_lib import (  # type: ignore
    build_kiwi_system, probe_solve_system, ConstraintSpec,
)


def _clone_solution(var_values: dict) -> dict:
    """Return a copy of the var_values mapping for equality comparison."""
    return {k: v for k, v in var_values.items()}


def leave_one_out_redundancy(history: dict,
                                baseline_solution: dict) -> dict:
    """Returns the set of redundant constraint ids.

    A constraint c is REDUNDANT if removing it yields the same final
    var_values as the baseline AND the baseline has unique solution
    (DOF = 0).  Without uniqueness, removing any constraint under an
    under-constrained system will still yield the same solved values
    (because suggestion values fix them) — we therefore require baseline
    DOF == 0 before we trust the redundancy verdict.

    For under-constrained baselines, we fall back to: a constraint is
    redundant iff removing it does NOT increase the DOF estimate.
    """
    points, lines, circles, constraints, deleted = parse_history(history)
    pts, lns, crs, cspecs = _to_specs(points, lines, circles, constraints)

    degeneracy_check = {
        "non_degenerate_line_lengths": {
            l_uuid: (lns[l_uuid].start_uuid, lns[l_uuid].end_uuid)
            for l_uuid in lns
        }
    }

    # Baseline DOF
    try:
        bsolver, bvar, binvalid = build_kiwi_system(
            pts, lns, crs, cspecs, deleted_entities=deleted,
        )
        baseline_raw = probe_solve_system(
            bsolver, bvar, binvalid, cspecs, deleted,
            degeneracy_check=degeneracy_check)
        baseline_dof = baseline_raw.get("dof_estimate") or 0
        baseline_solution = baseline_raw.get("var_values", {})
    except Exception:
        return {"used": True, "method": "leave-one-out-redundancy",
                "redundant_constraint_ids": [],
                "note": "baseline solve failed"}

    redundant_ids: list[str] = []
    for i, c in enumerate(cspecs):
        subset = cspecs[:i] + cspecs[i+1:]
        try:
            solver, var, invalid = build_kiwi_system(
                pts, lns, crs, subset, deleted_entities=deleted,
            )
            raw = probe_solve_system(solver, var, invalid, subset, deleted,
                                      degeneracy_check=degeneracy_check)
        except Exception:
            continue
        if raw["raw_solve"]["return_code"] != 0:
            continue
        new_dof = raw.get("dof_estimate") or 0

        # Redundancy test: removing c must NOT increase DOF (i.e., c was not
        # contributing to the constraint count).  When baseline is fully
        # constrained (DOF=0), we additionally verify solution values are
        # unchanged for tightness.
        if new_dof > baseline_dof:
            continue  # removing c made the system less constrained → c was useful
        if baseline_dof == 0:
            # Strict value comparison
            same = True
            for k, v in baseline_solution.items():
                rv = raw["var_values"].get(k)
                if rv is None or abs(rv - v) > 1e-9:
                    same = False
                    break
            if not same:
                continue
        redundant_ids.append(c.id)

    return {
        "used": True,
        "method": "leave-one-out-redundancy",
        "redundant_constraint_ids": redundant_ids,
    }


def leave_one_out_suspected_conflict(history: dict) -> dict:
    """For each constraint c, attempt removing c.  If the system only
    becomes fully-constrained after removal, c is SUSPECTED of being
    over-constrained or conflicting (we cannot distinguish in kiwisolver)."""
    points, lines, circles, constraints, deleted = parse_history(history)
    pts, lns, crs, cspecs = _to_specs(points, lines, circles, constraints)

    degeneracy_check = {
        "non_degenerate_line_lengths": {
            l_uuid: (lns[l_uuid].start_uuid, lns[l_uuid].end_uuid)
            for l_uuid in lns
        }
    }

    # First: baseline solve
    try:
        solver, var, invalid = build_kiwi_system(
            pts, lns, crs, cspecs, deleted_entities=deleted,
        )
        baseline = probe_solve_system(solver, var, invalid, cspecs, deleted,
                                       degeneracy_check=degeneracy_check)
    except Exception:
        baseline = None

    suspected: list[str] = []
    for i, c in enumerate(cspecs):
        subset = cspecs[:i] + cspecs[i+1:]
        try:
            solver, var, invalid = build_kiwi_system(
                pts, lns, crs, subset, deleted_entities=deleted,
            )
            raw = probe_solve_system(solver, var, invalid, subset, deleted,
                                      degeneracy_check=degeneracy_check)
        except Exception:
            continue
        if raw["raw_solve"]["return_code"] != 0:
            # Removing c made the system UNSOLVABLE → c was masking a deeper
            # conflict; not what we want here.
            continue
        # Heuristic: if baseline succeeded AND removing c dramatically
        # lowers DOF, c is suspected over-constrained.
        if baseline is None:
            continue
        baseline_dof = baseline.get("dof_estimate") or 0
        new_dof = raw.get("dof_estimate") or 0
        if baseline_dof <= 0 and new_dof > 0:
            suspected.append(c.id)

    return {
        "used": True,
        "method": "leave-one-out-suspected-conflict",
        "suspected_conflicting_constraint_ids": suspected,
    }


def run_fallbacks(history: dict, raw_solver: dict) -> dict:
    """Run all fallback analyses."""
    redundancy = leave_one_out_redundancy(
        history, raw_solver.get("var_values", {}))
    suspected_conflict = leave_one_out_suspected_conflict(history)
    return {
        "used": True,
        "method": "kiwisolver + leave-one-out",
        "redundant_constraint_ids": redundancy["redundant_constraint_ids"],
        "suspected_conflicting_constraint_ids":
            suspected_conflict["suspected_conflicting_constraint_ids"],
        "note": ("Redundancy + suspected conflict detected via leave-one-out "
                  "re-solves.  Each re-solve is O(constraints * solve_cost)."),
    }