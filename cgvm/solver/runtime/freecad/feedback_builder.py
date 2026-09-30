"""feedback_builder.py — Generate LLM-facing repair feedback (Layer 4).

Same as Kiwisolver_feedback.feedback_builder — produces
  summary, blocking_errors, warnings, suggested_actions, do_not_change.

We can use the same logic because the Layer 2 normalized state is
backend-agnostic.
"""
from __future__ import annotations

from typing import Any


def build_llm_feedback(normalized: dict,
                         constraint_diagnostics: dict,
                         fallback: dict,
                         recompute: dict) -> dict:
    summary_parts: list[str] = []
    blocking: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []
    do_not: list[str] = []

    status = normalized.get("solve_status", "unknown")
    severity = normalized.get("severity", "error")
    flags = normalized.get("flags", {})

    # 1. Conflict / unsolvable
    if status in ("conflicting", "unsolvable"):
        semantic = constraint_diagnostics.get("conflicting_constraints", [])
        if semantic:
            summary_parts.append(
                f"Sketch is conflicting: {len(semantic)} constraint(s) in conflict "
                "(detected by FreeCAD solver).")
            for c in semantic:
                blocking.append(c.get("description", str(c)))
                actions.append(
                    f"Resolve constraint {c.get('id')}: remove one of the "
                    "conflicting constraints or rewrite the geometry.")
        else:
            # FreeCAD reported a non-zero return code but did not surface a
            # structured Conflicting list (e.g., a line collapsed to a point).
            summary_parts.append(
                "Sketch is conflicting (FreeCAD solver reported a non-zero "
                "return code; no structured conflict list was emitted).")
            blocking.append(
                "FreeCAD solver failed to solve the sketch; "
                "inspect the constraint set manually for semantic conflicts.")
            actions.append("Remove or relax one of the conflicting constraints.")

    # 2. Invalid constraints
    if status == "invalid_constraint_reference":
        invalid = constraint_diagnostics.get("invalid_constraints", [])
        summary_parts.append(
            f"Sketch references {len(invalid)} invalid / malformed geometry id(s).")
        for inv in invalid:
            blocking.append(inv.get("description", str(inv)))
            actions.append(
                f"Recreate the referenced geometry or replace the constraint "
                "with a valid one.")

    # 3. Redundant
    if flags.get("has_redundancy") or flags.get("has_partially_redundant"):
        redundant = constraint_diagnostics.get("redundant_constraints", [])
        summary_parts.append(
            f"Sketch contains {len(redundant)} redundant constraint(s) "
            "(FreeCAD solver detected).")
        for r in redundant:
            warnings.append(
                f"Constraint {r.get('id')} ({r.get('type')}) is {r.get('type')}; "
                "removing it does not change the solved geometry.")

    # 4. Under / over-constrained
    if status == "under_constrained":
        summary_parts.append(
            f"Sketch is under-constrained (DOF={normalized.get('dof')}). "
            "Some dimensions are not pinned by any constraint.")
        warnings.append(
            f"Sketch is under-constrained (DOF={normalized.get('dof')}). "
            "The CAD result may differ from the Design Plan's intended dimensions.")
        actions.append(
            "Add dimension constraints (LinearDimension / DiameterDimension) "
            "to lock the geometry to the values specified in the Design Plan.")

    if status == "over_constrained":
        summary_parts.append(
            f"Sketch is over-constrained (DOF={normalized.get('dof')}). "
            "Some constraints are silently ignored.")
        warnings.append(
            f"Sketch is over-constrained (DOF={normalized.get('dof')}). "
            "The solver may have silently chosen an arbitrary solution.")
        actions.append(
            "Remove redundant or over-specified constraints; ensure each "
            "geometric parameter is constrained exactly once.")

    # 5. Recompute failure
    rc_status = recompute.get("recompute_status", "unknown")
    if rc_status == "failed":
        ff = recompute.get("failed_features", [])
        summary_parts.append(
            f"Document recompute failed: {len(ff)} feature(s) in Invalid state.")
        for f in ff:
            blocking.append(f"{f['name']}: {f['reason']}")
            actions.append(
                f"Fix feature {f['name']}: {f['reason']}.")

    # 6. Non-linear (untranslatable) constraints
    nl = normalized.get("non_linear_constraint_ids") or []
    if nl:
        warnings.append(
            f"{len(nl)} constraint(s) of type Parallel/Perpendicular/Tangent "
            "could not be directly translated from Fusion360 to FreeCAD; "
            "they are skipped during sketch construction.")

    # 7. Defaults
    do_not.extend([
        "Do not change geometry dimensions that are required by the Design Plan.",
        "Do not remove unrelated constraints.",
    ])

    if status == "fully_constrained" and severity == "pass" and not flags.get("has_conflict"):
        summary_parts = ["Sketch solved successfully — fully constrained, no conflicts detected."]
        blocking = []
        warnings = []
        actions = []

    summary = " ".join(summary_parts) if summary_parts else "Unknown solver state."

    return {
        "summary": summary,
        "blocking_errors": blocking,
        "warnings": warnings,
        "suggested_actions": actions,
        "do_not_change": do_not,
    }