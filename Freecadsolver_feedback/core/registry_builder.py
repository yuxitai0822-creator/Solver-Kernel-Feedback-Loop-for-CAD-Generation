"""registry_builder.py — Build geometry + constraint registry.

For FreeCAD, we use the actual sketch object (post-build) to enumerate
its Constraints and Geometry.  This is more reliable than introspecting
the original history JSON because FreeCAD may have pruned or replaced
constraints during solve.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def build_registry_from_state(raw_solver: dict) -> dict:
    """Build the registry dict from a raw_solver result.

    `raw_solver["constraints_summary"]` contains per-constraint info
    (index, type, first/second/third GeoId, value).
    `raw_solver["geometry_count"]` is the int count.
    """
    cs = raw_solver.get("constraints_summary", []) or []
    n_geom = int(raw_solver.get("geometry_count", 0))

    # Geometry registry: free-form placeholders (FreeCAD doesn't expose
    # geometry-by-uuid post-build).  V0.1 records count and stub entries.
    geom: dict[str, dict] = {}
    for i in range(n_geom):
        geom[f"geometry:{i}"] = {
            "type": "unknown",
            "construction": False,
        }

    cons: dict[str, dict] = {}
    for c in cs:
        cid = f"c{c['index']}"
        cons[cid] = {
            "type": c.get("type", "Unknown"),
            "entities": [c.get("first"), c.get("second"), c.get("third")],
            "value": c.get("value"),
        }

    return {
        "geometry_registry": geom,
        "constraint_registry": cons,
        "num_geometries": len(geom),
        "num_constraints": len(cons),
    }


def build_registry(history: dict) -> dict:
    """Convenience: build registry from a history JSON via solver_runner."""
    from core.solver_runner import run_solver_from_history
    raw = run_solver_from_history(history)
    return build_registry_from_state(raw)