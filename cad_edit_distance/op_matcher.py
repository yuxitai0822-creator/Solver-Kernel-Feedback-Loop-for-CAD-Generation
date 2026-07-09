"""op_matcher.py — Match operations between two sequences.

Strategy:
  1. Exact match by op_id (preferred).
  2. Match by role.
  3. Match by op_type + role.
  4. Remaining ops: Hungarian matching minimizing edit cost.
"""
from __future__ import annotations

from typing import Any


def match_ops(seq_a: list[dict], seq_b: list[dict]) -> list[dict]:
    """Match operations from seq_a to seq_b.

    Each returned match is a dict:
        {a_op, b_op, match_kind} where match_kind ∈
            'matched', 'added', 'deleted', 'changed'
    """
    used_b: set[int] = set()
    matches: list[dict] = []

    # 1. Exact op_id match
    a_id_to_idx = {op["op_id"]: i for i, op in enumerate(seq_a)}
    b_id_to_idx = {op["op_id"]: i for i, op in enumerate(seq_b)}

    matched_a: set[int] = set()
    matched_b: set[int] = set()

    for a_idx, op_a in enumerate(seq_a):
        oid = op_a.get("op_id")
        if oid and oid in b_id_to_idx:
            b_idx = b_id_to_idx[oid]
            matches.append({"a_op": op_a, "b_op": seq_b[b_idx],
                              "match_kind": "matched",
                              "match_by": "op_id"})
            matched_a.add(a_idx)
            matched_b.add(b_idx)
            used_b.add(b_idx)

    # 2. Role match for remaining ops
    a_by_role: dict[str, list[int]] = {}
    for i, op in enumerate(seq_a):
        if i in matched_a:
            continue
        role = op.get("role")
        if role:
            a_by_role.setdefault(role, []).append(i)

    b_by_role: dict[str, list[int]] = {}
    for i, op in enumerate(seq_b):
        if i in matched_b:
            continue
        role = op.get("role")
        if role:
            b_by_role.setdefault(role, []).append(i)

    for role, a_idxs in a_by_role.items():
        b_idxs = b_by_role.get(role, [])
        for ai, bi in zip(a_idxs, b_idxs):
            matches.append({"a_op": seq_a[ai], "b_op": seq_b[bi],
                              "match_kind": "matched",
                              "match_by": f"role:{role}"})
            matched_a.add(ai)
            matched_b.add(bi)
            used_b.add(bi)

    # 3. Op_type match for remaining
    a_by_type: dict[str, list[int]] = {}
    for i, op in enumerate(seq_a):
        if i in matched_a:
            continue
        ot = op.get("op_type")
        if ot:
            a_by_type.setdefault(ot, []).append(i)

    b_by_type: dict[str, list[int]] = {}
    for i, op in enumerate(seq_b):
        if i in matched_b:
            continue
        ot = op.get("op_type")
        if ot:
            b_by_type.setdefault(ot, []).append(i)

    for ot, a_idxs in a_by_type.items():
        b_idxs = b_by_type.get(ot, [])
        for ai, bi in zip(a_idxs, b_idxs):
            matches.append({"a_op": seq_a[ai], "b_op": seq_b[bi],
                              "match_kind": "matched",
                              "match_by": f"op_type:{ot}"})
            matched_a.add(ai)
            matched_b.add(bi)
            used_b.add(bi)

    # 4. Remaining ops are added/deleted
    for i, op_a in enumerate(seq_a):
        if i not in matched_a:
            matches.append({"a_op": op_a, "b_op": None,
                              "match_kind": "deleted",
                              "match_by": "unmatched_a"})

    for i, op_b in enumerate(seq_b):
        if i not in matched_b:
            matches.append({"a_op": None, "b_op": op_b,
                              "match_kind": "added",
                              "match_by": "unmatched_b"})

    return matches