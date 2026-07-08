"""recompute_runner.py — Detect downstream feature failures via doc.recompute().

FreeCAD provides direct doc.recompute() which:
  * raises an exception if recompute fails (rare),
  * sets feature.State = ['Touched', 'Invalid'] on a feature whose
    recompute failed silently.

V0.1 recompute detection uses BOTH signals:
  1. recompute_exception — Python exception thrown by recompute()
  2. pad_invalid (or any feature in state 'Invalid')

Returns dict in the same format as Kiwisolver_feedback's recompute_runner
for API compatibility:
    {
      'status': 'success' | 'failed' | 'skipped' | 'unknown',
      'failed_features': [{'name': str, 'reason': str}, ...],
      'message': str | None
    }
"""
from __future__ import annotations

from typing import Any


def run_recompute_from_state(raw_solver: dict) -> dict:
    """Build a recompute verdict from raw solver feedback (post-solve state).

    The raw_solver dict contains:
      * recompute_success: bool — was doc.recompute() called without exception?
      * recompute_exception: str|None — error message if it raised
      * pad_invalid: bool — Pad.State contains 'Invalid'
      * pad_state: list[str] — full Pad.State
      * pad_length: float — current Length value
    """
    failed: list[dict] = []
    if not raw_solver.get("recompute_success", True):
        failed.append({
            "name": "Document",
            "reason": raw_solver.get("recompute_exception", "recompute raised"),
        })
    if raw_solver.get("pad_invalid"):
        failed.append({
            "name": "Pad",
            "reason": (f"Pad.Length={raw_solver.get('pad_length', '?')} is invalid; "
                          f"Pad.State={raw_solver.get('pad_state')}"),
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
        "message": "doc.recompute() succeeded; no feature in Invalid state",
    }