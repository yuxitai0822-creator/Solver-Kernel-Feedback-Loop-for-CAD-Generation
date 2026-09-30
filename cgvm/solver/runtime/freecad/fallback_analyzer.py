"""fallback_analyzer.py — No-op for FreeCAD backend.

FreeCAD Sketcher exposes RedundantConstraints, ConflictingConstraints,
MalformedConstraints, PartiallyRedundantConstraints, etc. directly.
Therefore the fallback_analyzer (leave-one-out tests) used in
Kiwisolver_feedback is NOT needed here.

This module is kept for API compatibility with the Kiwisolver_feedback
pipeline so the downstream modules (diagnostics_builder, feedback_builder)
can be reused unchanged.

If additional fallback analysis is ever needed in the FreeCAD backend
(e.g., for non-linear constraints), it can be added here.
"""
from __future__ import annotations

from typing import Any


def run_fallbacks(history: dict, raw_solver: dict) -> dict:
    """No-op for FreeCAD.  Returns an empty fallback result."""
    return {
        "used": False,
        "method": None,
        "redundant_constraint_ids": [],
        "suspected_conflicting_constraint_ids": [],
        "note": "FreeCAD Sketcher exposes RedundantConstraints and "
                 "ConflictingConstraints directly; no leave-one-out fallback "
                 "is needed.",
    }