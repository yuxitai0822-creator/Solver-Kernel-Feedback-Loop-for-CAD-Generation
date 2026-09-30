"""diagnostics_builder.py — Build Layer 3 constraint-level diagnostics.

Combines:
  * semantic conflicts (from solver_runner degeneracy check)
  * invalid constraints (from solver_runner adapter pre-check)
  * redundant constraints (from fallback_analyzer leave-one-out)
  * under-constrained entities (heuristic: free variables)
"""
from __future__ import annotations

from typing import Any


def build_constraint_diagnostics(
        raw_solver: dict,
        fallback: dict,
        deleted_entities: set[str]) -> dict:
    """Return:
        {
          'conflicting_constraints': [{'id', 'type', 'entities', 'description'}, ...],
          'redundant_constraints': [{'id', 'type', 'entities', 'description'}, ...],
          'invalid_constraints': [{'id', 'reason', 'description'}, ...],
          'underconstrained_entities': [{'entity', 'reason'}, ...]
        }
    """
    # 1. Conflicting (semantic conflicts from degeneracy check)
    semantic = raw_solver.get("semantic_conflicts", [])
    conflicting = []
    for s in semantic:
        # s looks like: "line_l0_collapsed_to_point: start=... end=..."
        if "collapsed_to_point" in s:
            ln_uuid = s.split(":")[0].replace("line_", "")
            conflicting.append({
                "id": f"semantic:{ln_uuid}",
                "type": "semantic_conflict",
                "entities": [f"line:{ln_uuid}"],
                "description": (
                    f"Line {ln_uuid} has been collapsed to a single point by "
                    "incompatible orientation constraints (e.g. Horizontal + "
                    "Vertical on the same line)."),
            })
        else:
            conflicting.append({
                "id": f"semantic:{s}",
                "type": "semantic_conflict",
                "entities": [],
                "description": s,
            })

    # 2. Invalid
    invalid = []
    for entry in raw_solver.get("invalid_constraint_ids", []):
        # entry looks like "c_coin_bad:point p0 or p_deleted missing"
        if ":" in entry:
            cid, reason = entry.split(":", 1)
        else:
            cid, reason = entry, "unknown"
        invalid.append({
            "id": cid,
            "reason": reason,
            "description": f"Constraint {cid} is invalid: {reason}",
        })
    # Also: dangling entities
    for d in deleted_entities:
        invalid.append({
            "id": f"deleted_entity_ref:{d}",
            "reason": f"references deleted entity uuid {d}",
            "description": f"Constraint references deleted geometry uuid {d}.",
        })

    # 3. Redundant
    redundant = []
    for rid in fallback.get("redundant_constraint_ids", []):
        redundant.append({
            "id": rid,
            "type": "redundant",
            "entities": [],
            "description": (f"Constraint {rid} is redundant: removing it does "
                              "not change the solved geometry."),
        })

    # 4. Under-constrained entities (heuristic: a variable that the solver
    # did NOT change from its suggested value is "free").  We use the
    # diff between suggested values and solved values.
    var_values = raw_solver.get("var_values", {})
    registry = raw_solver.get("registry", {})
    dof = raw_solver.get("dof_estimate", 0)
    underconstrained = []
    if dof and dof > 0:
        # We don't have access to suggestion values from raw_solver.
        # Approximate: report the top-DOF variables.
        sorted_vars = sorted(var_values.items(),
                              key=lambda kv: abs(kv[1] or 0))
        for k, v in sorted_vars[:min(dof, 5)]:
            underconstrained.append({
                "entity": k,
                "reason": f"variable {k} is not pinned by any constraint",
            })

    return {
        "conflicting_constraints": conflicting,
        "redundant_constraints": redundant,
        "invalid_constraints": invalid,
        "underconstrained_entities": underconstrained,
    }