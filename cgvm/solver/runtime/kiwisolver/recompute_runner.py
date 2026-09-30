"""recompute_runner.py — Detect downstream feature failures.

The frozen kiwisolver backend is sketch-only; downstream CAD features
(ExtrudeFeature, Pad, Pocket, etc.) are validated by per-feature sanity
rules because no document-level recompute API is available.

Sanity rules for V0.1:
  * ExtrudeFeature.extent_one.distance.value > 0
  * Sketch consumed profile has at least 1 outer loop
  * No degenerate circles (radius > 0)

If any rule fails, recompute is marked failed and the offending feature is
recorded in `failed_features`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_recompute(history: dict) -> dict:
    """Return:
        {
          'status': 'success' | 'failed' | 'skipped' | 'unknown',
          'failed_features': [{'name': str, 'reason': str}, ...],
          'message': str | None
        }
    """
    entities = history.get("entities", {})
    timeline = history.get("timeline", [])
    sketch = extrude = None
    for ev in timeline:
        e = entities.get(ev.get("entity", ""), {})
        if e.get("type") == "Sketch" and sketch is None:
            sketch = e
        elif e.get("type") == "ExtrudeFeature" and extrude is None:
            extrude = e

    failed: list[dict] = []

    # Rule 1: extrude distance must be > 0
    if extrude is not None:
        eo = extrude.get("extent_one") or {}
        d = (eo.get("distance") or {}).get("value") if isinstance(eo, dict) else 0
        if d is None or d <= 0:
            failed.append({
                "name": "ExtrudeFeature",
                "reason": f"extrude.distance.value={d!r} is not positive"
            })
        # Rule 2: extent_type must be one of the 3 supported
        et = extrude.get("extent_type", "")
        if et not in ("OneSideFeatureExtentType",
                      "SymmetricFeatureExtentType",
                      "TwoSidesFeatureExtentType"):
            failed.append({
                "name": "ExtrudeFeature",
                "reason": f"unsupported extent_type={et!r}"
            })
    else:
        failed.append({
            "name": "ExtrudeFeature",
            "reason": "no ExtrudeFeature entity in timeline"
        })

    # Rule 3: at least one consumed profile
    if extrude is not None:
        consumed = extrude.get("profiles") or []
        if not consumed:
            failed.append({
                "name": "ExtrudeFeature",
                "reason": "extrude.profiles is empty"
            })

    # Rule 4: sketch has at least one profile
    if sketch is None:
        failed.append({
            "name": "Sketch",
            "reason": "no Sketch entity in timeline"
        })
    else:
        if not sketch.get("profiles"):
            failed.append({
                "name": "Sketch",
                "reason": "sketch has no profiles"
            })
        # Rule 5: every SketchCircle has positive radius
        for cid, c in sketch.get("curves", {}).items():
            if c.get("type") == "SketchCircle":
                r = c.get("radius")
                if r is None or r <= 0:
                    failed.append({
                        "name": f"SketchCircle:{cid}",
                        "reason": f"circle radius={r!r} is not positive"
                    })

    if failed:
        return {
            "status": "failed",
            "failed_features": failed,
            "message": "; ".join(f"{f['name']}: {f['reason']}" for f in failed),
        }
    return {
        "status": "success",
        "failed_features": [],
        "message": "all downstream feature sanity rules passed",
    }