"""registry_builder.py — Build the geometry + constraint registry.

Produces the JSON-shaped registry the spec calls for in Layer 2.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.history_parser import parse_history


def build_registry(history: dict) -> dict:
    """Return:
        {
          'geometry_registry': {
            'point_uuid': {'type': 'Point', 'x': float, 'y': float, 'construction': False},
            'line_uuid':   {'type': 'Line',  'start': uuid, 'end': uuid, 'construction': bool},
            ...
          },
          'constraint_registry': {
            'c_uuid': {
              'type': 'Horizontal' | 'Vertical' | ...,
              'entities': [uuid, uuid, ...],
              'value': float | None
            },
            ...
          },
          'num_geometries': int,
          'num_constraints': int
        }
    """
    points, lines, _, constraints, _ = parse_history(history)

    geom: dict[str, dict] = {}
    for uid, p in points.items():
        geom[f"pt:{uid}"] = {
            "type": "Point",
            "x": p["x"],
            "y": p["y"],
            "construction": False,
        }
    for uid, l in lines.items():
        geom[f"line:{uid}"] = {
            "type": "Line",
            "start": f"pt:{l['start']}",
            "end": f"pt:{l['end']}",
            "construction": l.get("construction", False),
        }

    cons: dict[str, dict] = {}
    for c in constraints:
        cons[c["id"]] = {
            "type": c["type"],
            "entities": list(c.get("entities") or []),
            "value": c.get("value"),
        }

    return {
        "geometry_registry": geom,
        "constraint_registry": cons,
        "num_geometries": len(geom),
        "num_constraints": len(cons),
    }