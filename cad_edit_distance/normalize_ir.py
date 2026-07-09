"""normalize_ir.py — Normalize an IR to a canonical operation-sequence form.

A normalized IR is a list of NormalizedOperation dicts with stable fields
the matcher and edit-cost module consume.  Field names are stable strings
(do not change between runs).
"""
from __future__ import annotations

import json
from typing import Any


def normalize_ir(ir: dict) -> dict:
    """Convert a parsed cad_ir_v0.1 dict to its normalized form.

    Returns dict with keys:
      sample_id, coordinate_system, operations
      where each op is:
        {op_id, op_type, role, input, params_normalized, base_weight}
    """
    return {
        "sample_id": ir.get("sample_id"),
        "schema_version": ir.get("schema_version"),
        "coordinate_system": ir.get("coordinate_system", {}),
        "operations": [
            _normalize_op(op) for op in ir.get("operations", [])
        ],
    }


def _normalize_op(op: dict) -> dict:
    """Normalize a single operation.  The `params_normalized` is a
    key-sorted, type-stable version of params suitable for diff."""
    p = dict(op.get("params") or {})
    # Round floats to 4 decimal places for stable matching
    p_norm = {}
    for k in sorted(p.keys()):
        v = p[k]
        if isinstance(v, float):
            v = round(v, 4)
        elif isinstance(v, list):
            # Normalize list of floats
            v = [round(x, 4) if isinstance(x, float) else x for x in v]
        p_norm[k] = v
    return {
        "op_id": op.get("op_id"),
        "op_type": op.get("op_type"),
        "role": op.get("role"),
        "input": op.get("input"),
        "params_normalized": p_norm,
        "base_weight": BASE_WEIGHTS.get(op.get("op_type"), 3),
    }


BASE_WEIGHTS = {
    "sketch_rectangle": 2,
    "sketch_circle": 2,
    "sketch_annulus": 2,
    "sketch_rectangular_frame": 2,
    "sketch_stadium": 2,
    "sketch_polygon": 2,
    "extrude": 3,
    "cut": 4,
    "join": 4,
    "add_constraint": 2,
    "set_dimension": 2,
    "export_step": 1,
}


def normalize_op_dicts(ops: list[dict]) -> list[dict]:
    """Convenience: just normalize a list of op dicts (no top-level IR)."""
    return [_normalize_op(op) for op in ops]


def total_weight(ops: list[dict]) -> int:
    """Total base-weight of a sequence of normalized ops."""
    return sum(op["base_weight"] for op in ops)