"""solver_runner.py — Production wrapper around kiwisolver + history_parser.

V0.1 uses kiwisolver as the 2D linear-constraint-solver backend.
The runner accepts a Fusion360 history JSON (via `run_solver_from_history`)
and returns a raw solver result dict (Layer 1 of the spec).

Output Layer 1 — Raw Solver Output:
    {
      'raw_solve': {return_code, exception, message},
      'var_values': {name: float, ...},
      'dof_estimate': int,
      'invalid_constraint_ids': [str, ...],
      'deleted_entities_referenced': [uuid, ...],
      'semantic_conflicts': [str, ...],
      'non_linear_constraints': [constraint_id, ...],
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
from api_probe.probe_lib import (  # type: ignore
    build_kiwi_system, probe_solve_system, PointSpec, LineSpec,
    ConstraintSpec,
)


def _to_specs(points: dict, lines: dict, circles: dict,
              constraints: list[dict]) -> tuple[dict, dict, dict, list]:
    """Adapt history-parser output into kiwisolver-compatible dataclasses."""
    pts = {uid: PointSpec(uid, p["x"], p["y"]) for uid, p in points.items()}
    lns = {uid: LineSpec(uid, l["start"], l["end"]) for uid, l in lines.items()}
    crs = circles  # already in dict form (empty in V0.1)
    cspecs = []
    for c in constraints:
        cspecs.append(ConstraintSpec(
            id=c["id"], type=c["type"],
            entities=list(c.get("entities") or []),
            value=c.get("value"),
        ))
    return pts, lns, crs, cspecs


def run_solver_from_history(history: dict) -> dict:
    """Top-level entry point: history JSON → raw solver result.

    Returns the dict described in the module docstring (Layer 1).
    """
    points, lines, circles, constraints, deleted = parse_history(history)
    pts, lns, crs, cspecs = _to_specs(points, lines, circles, constraints)

    # Build degeneracy-check map: every line → (start_pt, end_pt)
    degeneracy_check: dict[str, dict] = {
        "non_degenerate_line_lengths": {
            l_uuid: (lns[l_uuid].start_uuid, lns[l_uuid].end_uuid)
            for l_uuid in lns
        }
    }

    solver, var, invalid = build_kiwi_system(
        pts, lns, crs, cspecs, deleted_entities=deleted,
    )

    # Detect non-linear (untranslatable) constraints
    non_linear_ids = [
        c.id for c in cspecs
        if c.type in ("Parallel", "Perpendicular", "Tangent")
    ]

    raw = probe_solve_system(solver, var, invalid, cspecs, deleted,
                              degeneracy_check=degeneracy_check)
    raw["non_linear_constraints"] = non_linear_ids
    raw["registry"] = {
        "num_points": len(pts),
        "num_lines": len(lns),
        "num_circles": len(crs),
        "num_constraints": len(cspecs),
    }
    return raw


def run_solver_from_json(path: str | Path) -> dict:
    """Convenience: load JSON file then run."""
    import json
    history = json.loads(Path(path).read_text(encoding="utf-8"))
    return run_solver_from_history(history)