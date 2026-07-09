"""edit_cost.py — Compute the cost of a single matched operation.

Cost table (from the task spec):
    numeric parameter edit               1
    non-numeric parameter edit          1.5
    constraint value edit               1
    constraint type edit                2
    target/reference edit               2
    add/delete constraint               2
    add/delete sketch primitive         2
    add/delete feature op               3
    profile type change                 4
    boolean operation change            4
    topology structure change           5
    full rewrite flag                   8

A `matched` op may have several costs combined.  A `changed` op has all
its deltas summed.  An `added`/`deleted` op uses the `add/delete <type>`
cost.
"""
from __future__ import annotations

from typing import Any


PROFILE_TYPE_OPS = {
    "sketch_rectangle", "sketch_circle", "sketch_annulus",
    "sketch_rectangular_frame", "sketch_stadium", "sketch_polygon",
}

FEATURE_OPS = {"extrude"}
CONSTRAINT_OPS = {"add_constraint"}
DIMENSION_OPS = {"set_dimension"}
BOOLEAN_OPS = {"cut", "join"}
TOPOLOGY_OPS = {"export_step"}


def match_cost(match: dict) -> float:
    """Compute the cost of a single matched-op entry.

    match: {a_op, b_op, match_kind, match_by}
    """
    kind = match["match_kind"]
    a_op = match["a_op"]
    b_op = match["b_op"]

    if kind == "added":
        if a_op is None and b_op is not None:
            ot = b_op["op_type"]
            return _add_delete_cost(ot)
        return 0.0
    if kind == "deleted":
        if b_op is None and a_op is not None:
            ot = a_op["op_type"]
            return _add_delete_cost(ot)
        return 0.0
    if kind == "matched":
        if a_op is None or b_op is None:
            return 0.0
        return _matched_cost(a_op, b_op)
    return 0.0


def _add_delete_cost(op_type: str) -> float:
    if op_type in CONSTRAINT_OPS:
        return 2.0
    if op_type in PROFILE_TYPE_OPS:
        return 2.0
    if op_type in FEATURE_OPS:
        return 3.0
    if op_type in BOOLEAN_OPS:
        return 4.0
    if op_type in TOPOLOGY_OPS:
        return 1.0  # export is cheap
    return 3.0


def _matched_cost(a_op: dict, b_op: dict) -> float:
    cost = 0.0
    # Profile type change
    if a_op["op_type"] != b_op["op_type"]:
        if (a_op["op_type"] in PROFILE_TYPE_OPS
                and b_op["op_type"] in PROFILE_TYPE_OPS):
            cost += 4.0  # profile type change
        elif a_op["op_type"] in BOOLEAN_OPS and b_op["op_type"] in BOOLEAN_OPS:
            cost += 4.0  # boolean operation change
        else:
            cost += 5.0  # topology structure change
        return cost

    ot = a_op["op_type"]
    a_p = a_op["params_normalized"]
    b_p = b_op["params_normalized"]

    if ot in CONSTRAINT_OPS:
        # Constraint type change is heavier than constraint value change
        if a_p.get("constraint_type") != b_p.get("constraint_type"):
            cost += 2.0  # constraint type edit
        else:
            cost += 1.0  # constraint value edit (counted once even with multiple fields)
        # Target / reference edit
        if a_p.get("target") != b_p.get("target"):
            cost += 2.0
        if a_p.get("entities") != b_p.get("entities"):
            cost += 2.0
        if a_p.get("value") != b_p.get("value"):
            cost += 1.0
        return cost

    if ot in DIMENSION_OPS:
        if a_p.get("dimension_type") != b_p.get("dimension_type"):
            cost += 2.0  # constraint type edit (dimension type)
        cost += _param_diff_cost(a_p, b_p,
                                  exclude=("target", "dimension_type"))
        if a_p.get("target") != b_p.get("target"):
            cost += 2.0
        if a_p.get("entity") != b_p.get("entity"):
            cost += 2.0
        return cost

    # Profile ops (rectangle, circle, annulus, frame, stadium, polygon)
    # + extrude + cut + join + export_step
    cost += _param_diff_cost(a_p, b_p)

    # input / dependency edit
    if a_op.get("input") != b_op.get("input"):
        cost += 2.0

    # role change (semantic)
    if a_op.get("role") != b_op.get("role"):
        cost += 1.5

    return cost


def _param_diff_cost(a_p: dict, b_p: dict, exclude: tuple = ()) -> float:
    """Sum numeric & non-numeric param diff costs."""
    cost = 0.0
    keys = set(a_p.keys()) | set(b_p.keys())
    for k in keys:
        if k in exclude:
            continue
        # export_step.path is not semantically part of CAD — exclude from
        # CAD-operation-level edit cost.
        if k == "path":
            continue
        if k not in a_p or k not in b_p:
            cost += 1.0
            continue
        a, b = a_p[k], b_p[k]
        if a == b:
            continue
        # Both numeric?
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            cost += 1.0
        elif isinstance(a, list) and isinstance(b, list):
            # Compare element-wise
            if len(a) != len(b):
                cost += 2.0
            else:
                for x, y in zip(a, b):
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        if x != y:
                            cost += 1.0
                    elif x != y:
                        cost += 1.5
        else:
            cost += 1.5  # non-numeric parameter edit
    return cost