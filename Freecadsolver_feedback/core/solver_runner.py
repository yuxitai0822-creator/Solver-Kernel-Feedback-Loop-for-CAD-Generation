"""solver_runner.py — Production wrapper around FreeCAD Sketcher.

Builds a FreeCAD sketch + document from a history JSON spec, runs
sketch.solve() and captures the raw solver state directly via
FreeCAD's official APIs:
  * sketch.DoF
  * sketch.RedundantConstraints
  * sketch.ConflictingConstraints
  * sketch.PartiallyRedundantConstraints
  * sketch.MalformedConstraints
  * sketch.solve() return code
  * sketch.Constraints / Geometry

Returns Layer 1 (raw) solver feedback dict.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api_probe"))

from core.history_parser import parse_history_to_sketch_spec
from api_probe.probe_lib import (
    get_modules, build_sketch, probe_sketch_state, LineSpec, ConstraintSpec,
    PadSpec,
)


def _spec_to_dataclasses(spec: dict) -> dict:
    """Translate spec dict → dataclasses for probe_lib."""
    return {
        "lines": [LineSpec(ln["uuid"], ln["start"], ln["end"])
                   for ln in spec.get("lines", [])],
        "constraints": [ConstraintSpec(
            type=c["type"],
            params=tuple(c.get("params") or ()),
            target_geo=c.get("target_geo", -1),
            target_pos=c.get("target_pos", -1),
        ) for c in spec.get("constraints", [])],
        "pad": PadSpec(**spec["pad"]) if spec.get("pad") else None,
    }


def run_solver_from_history(history: dict) -> dict:
    """Top-level entry: history JSON → raw solver feedback dict (Layer 1)."""
    spec = parse_history_to_sketch_spec(history)
    non_linear = spec.get("non_linear", [])
    deleted = spec.get("deleted_entities", set())
    dc = _spec_to_dataclasses(spec)

    # If there are no lines, return empty state.
    if not dc["lines"]:
        return {
            "raw_solve": {"return_code": -1, "exception": "no lines in sketch",
                          "message": "no SketchLine entities found"},
            "dof": 0,
            "invalid_constraint_ids": [],
            "deleted_entities_referenced": sorted(deleted),
            "semantic_conflicts": [],
            "non_linear_constraint_ids": list(non_linear),
            "registry": {"num_points": 0, "num_lines": 0, "num_circles": 0,
                          "num_constraints": 0},
        }

    try:
        result = build_sketch(dc)
        state = probe_sketch_state(result['doc'], result['sketch'],
                                       pad=result.get('pad'))
    except Exception as e:
        return {
            "raw_solve": {"return_code": -1,
                          "exception": f"{type(e).__name__}: {e}",
                          "message": "build_sketch failed"},
            "dof": 0,
            "invalid_constraint_ids": [],
            "deleted_entities_referenced": sorted(deleted),
            "semantic_conflicts": [],
            "non_linear_constraint_ids": list(non_linear),
            "registry": {"num_points": 0, "num_lines": len(dc["lines"]),
                          "num_circles": 0,
                          "num_constraints": len(dc["constraints"])},
        }

    state["deleted_entities_referenced"] = sorted(deleted)
    state["non_linear_constraint_ids"] = list(non_linear)
    state["registry"] = {
        "num_points": 0,  # not tracked separately in V0.1
        "num_lines": state.get("geometry_count", 0),
        "num_circles": 0,
        "num_constraints": state.get("constraint_count", 0),
    }
    return state


def run_solver_from_json(path: str | Path) -> dict:
    """Convenience: load JSON file then run."""
    history = json.loads(Path(path).read_text(encoding="utf-8"))
    return run_solver_from_history(history)