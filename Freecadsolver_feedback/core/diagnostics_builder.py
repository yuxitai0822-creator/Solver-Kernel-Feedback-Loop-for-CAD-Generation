"""diagnostics_builder.py — Build Layer 3 constraint-level diagnostics.

For the FreeCAD backend, the diagnostics are populated DIRECTLY from
FreeCAD's solver state (no heuristics needed).  We translate each
flagged constraint index into a structured diagnostic entry.
"""
from __future__ import annotations

from typing import Any


def build_constraint_diagnostics(raw_solver: dict,
                                    fallback: dict,
                                    deleted_entities: set) -> dict:
    """Layer 3 — structured constraint-level diagnostics.

    Returns dict with keys:
        conflicting_constraints: [{id, type, entities, description}, ...]
        redundant_constraints: [{id, type, entities, description}, ...]
        invalid_constraints: [{id, reason, description}, ...]
        underconstrained_entities: [{entity, reason}, ...]
    """
    cs = raw_solver.get("constraints_summary", []) or []
    # Map index → type for description.
    idx_to_type = {c["index"]: c["type"] for c in cs}
    # Map index → entities (first, second, third).
    idx_to_ents = {c["index"]: [c.get("first"), c.get("second"), c.get("third")]
                    for c in cs}

    # 1. Conflicting
    conflicting = []
    for idx in raw_solver.get("conflicting_constraints", []):
        conflicting.append({
            "id": f"c{idx}",
            "type": "conflicting",
            "entities": idx_to_ents.get(idx, []),
            "description": (f"Constraint c{idx} ({idx_to_type.get(idx, '?')}) "
                              "is part of a conflicting constraint set "
                              "(FreeCAD solver detected)"),
        })

    # 2. Redundant
    redundant = []
    for idx in raw_solver.get("redundant_constraints", []):
        redundant.append({
            "id": f"c{idx}",
            "type": "redundant",
            "entities": idx_to_ents.get(idx, []),
            "description": (f"Constraint c{idx} ({idx_to_type.get(idx, '?')}) "
                              "is redundant — removing it does not change the "
                              "solved geometry"),
        })
    # Partially redundant
    for idx in raw_solver.get("partially_redundant_constraints", []):
        if idx not in raw_solver.get("redundant_constraints", []):
            redundant.append({
                "id": f"c{idx}",
                "type": "partially_redundant",
                "entities": idx_to_ents.get(idx, []),
                "description": (f"Constraint c{idx} ({idx_to_type.get(idx, '?')}) "
                                  "is partially redundant (relaxes the system "
                                  "but is not strictly implied)"),
            })

    # 3. Malformed / invalid
    invalid = []
    for idx in raw_solver.get("malformed_constraints", []):
        invalid.append({
            "id": f"c{idx}",
            "reason": "malformed_constraint",
            "description": (f"Constraint c{idx} ({idx_to_type.get(idx, '?')}) "
                              "is malformed (FreeCAD solver rejected)"),
        })
    # Dangling entities
    for d in deleted_entities:
        invalid.append({
            "id": f"deleted_entity_ref:{d}",
            "reason": f"references deleted geometry uuid {d}",
            "description": f"Constraint references deleted geometry uuid {d}.",
        })

    # 4. Under-constrained entities
    dof = raw_solver.get("dof", 0)
    underconstrained = []
    if dof > 0:
        underconstrained.append({
            "entity": "sketch",
            "reason": (f"sketch has {dof} degree(s) of freedom; "
                          f"geometry is not fully pinned by constraints"),
        })
    # Missing Vertical/Horizontal
    missing_vh = raw_solver.get("missing_vertical_horizontal_constraints", [])
    for idx in missing_vh:
        underconstrained.append({
            "entity": f"geometry:{idx}",
            "reason": (f"geometry {idx} lacks a Vertical/Horizontal constraint "
                          "(might be intended as a diagonal)"),
        })

    return {
        "conflicting_constraints": conflicting,
        "redundant_constraints": redundant,
        "invalid_constraints": invalid,
        "underconstrained_entities": underconstrained,
    }