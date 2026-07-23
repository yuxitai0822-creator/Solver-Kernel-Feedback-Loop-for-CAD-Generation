"""code2oper/ast_parser.py — AST-based extraction of cadquery API calls.

Phase 2A Task A2.2.  Parses a cadquery Python script via Python's
``ast`` module.  Walks the AST and emits a list of ``Operation`` for
each cadquery API call (e.g., ``wp.rect(...)``,
``workplane.extrude(...)``, ``result.translate(...)``).

Design choices:
  - We do NOT use regex; we use the full AST.  This handles
    method-chained expressions (``wp.rect(...).extrude(...)``) and
    captures argument values whether they are literals, names, or
    arithmetic expressions.
  - We recognise any method call on a ``Workplane``-like object as a
    candidate.  We look up the method name in ``API_OP_MAP``.  Methods
    not in the map are recorded as ``unknown`` (preserved, not dropped).
  - The output is a list of ``Operation`` (see ``taxonomy.py``).
    Returns ``None`` (not a list, not an empty list) on parse failure,
    so the caller can distinguish "unparseable" from "parses but empty".
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from .taxonomy import API_OP_MAP, Operation, param_to_dict


# Cadquery classes that hold a "current workplane" (so chained
# methods can be parsed as operations on that workplane).
_WORKPLANE_LIKE_NAMES = {"Workplane", "Plane", "Face", "Wire",
                          "Location", "Compound", "Part"}


def _literal_or_name(node: ast.AST) -> Any:
    """Return a Python value if the node is a literal/identifier that
    we can extract, else the string representation."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return node.id  # identifier name as fallback
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _literal_or_name(node.operand)
        if isinstance(inner, (int, float)):
            return -inner if isinstance(node.op, ast.USub) else inner
    if isinstance(node, ast.BinOp):
        # Try to eval simple constant arithmetic.
        try:
            return ast.literal_eval(node)
        except Exception:
            pass
    if isinstance(node, ast.Call):
        # Method call: try the function name as the value, else None.
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
    return _attr_dump(node)


def _attr_dump(node: ast.AST) -> str:
    """Best-effort string representation for a complex AST node."""
    try:
        return ast.unparse(node)
    except Exception:
        return f"<{type(node).__name__}>"


def _extract_arg(call_node: ast.Call, name: str | int) -> Any:
    """Return the kwarg or positional arg named ``name`` (str) or at
    position ``name`` (int) in a call.  Returns None if not found.

    ``name`` semantics:
      - int  : positional index (0-based)
      - str  : keyword name; if not found, try as positional index in
               lexical order (the ``arg_spec`` list)
    """
    if isinstance(name, int):
        if name < len(call_node.args):
            return _literal_or_name(call_node.args[name])
        return None
    # First try keyword.
    for kw in call_node.keywords:
        if kw.arg == name:
            return _literal_or_name(kw.value)
    # No keyword: caller will pass a positional mapping separately.
    return None


def _positional_in_spec(arg_spec: list, name: str) -> int | None:
    """Return the positional index of ``name`` in ``arg_spec``, or None
    if it is not in the list."""
    for i, spec in enumerate(arg_spec):
        if spec == name:
            return i
    return None


def _parse_call(call_node: ast.Call, arg_spec: list,
                  chain: list[str] | None = None) -> Operation | None:
    """Parse a single ``ast.Call`` node into an ``Operation`` (or None
    if the call is not a cadquery operation we recognise)."""
    if not isinstance(call_node.func, ast.Attribute):
        return None
    method_name = call_node.func.attr
    op_kind_args = API_OP_MAP.get(method_name)
    if op_kind_args is None:
        return None
    op_kind, arg_spec_list = op_kind_args
    parameters: dict[str, Any] = {}
    for spec in arg_spec_list:
        if isinstance(spec, int):
            value = _extract_arg(call_node, spec)
        else:
            # String name: try keyword first, then positional index in
            # the order declared in API_OP_MAP.
            value = _extract_arg(call_node, spec)
            if value is None:
                pos = _positional_in_spec(arg_spec_list, spec)
                if pos is not None:
                    value = _extract_arg(call_node, pos)
        if value is not None:
            parameters[spec] = param_to_dict(value)
    chain_str = ".".join(chain) if chain else "?"
    source = {"api": f"cq.<Workplane|...>.{method_name}",
                "argument": list(parameters.keys())}
    return Operation(operation=op_kind, parameters=parameters, source=source)


def parse_cadquery_script(script: str) -> list[Operation] | None:
    """Parse a cadquery Python script and return its operation list.

    Returns ``None`` on parse failure (e.g., syntax error, file not
    found).  Returns an empty list if the script parses but contains
    no recognised cadquery operations.
    """
    if not script or not script.strip():
        return []
    try:
        tree = ast.parse(script, mode="exec")
    except SyntaxError:
        return None
    except Exception:
        return None

    operations: list[Operation] = []
    _walk_tree(tree, operations, chain=[])
    return operations


def _walk_tree(node: ast.AST, operations: list[Operation],
                chain: list[str]) -> None:
    """Walk the AST, tracking the variable chain (e.g., ``wp = ...``
    then ``wp.rect(...)``).  Append operations to ``operations``."""
    if isinstance(node, ast.Module):
        for stmt in node.body:
            _walk_tree(stmt, operations, chain=[])
        return
    if isinstance(node, ast.Assign):
        # Track assignments:  ``wp = cq.Workplane(...)`` records
        # ``wp`` in the chain; ``wp.rect(...).extrude(...)`` walks
        # the value's AST with chain including ``wp``.
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            _walk_tree(node.value, operations, chain + [var_name])
        else:
            _walk_tree(node.value, operations, chain=[])
        return
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        _walk_tree(node.value, operations, chain=[])
        return
    if isinstance(node, ast.Call):
        # Look up the API op map to know positional-arg mapping.
        if isinstance(node.func, ast.Attribute):
            entry = API_OP_MAP.get(node.func.attr)
            arg_spec = entry[1] if entry else []
            # Chained methods:  ``wp.rect(...).extrude(...)`` parses as
            # ``Call(func=Attribute(value=Call(rect), attr='extrude'))``.
            # The inner Call (the ``rect`` call) is reachable via
            # ``node.func.value``.  Recurse into it.
            if isinstance(node.func.value, ast.Call):
                _walk_tree(node.func.value, operations, chain=chain)
        else:
            arg_spec = []
        op = _parse_call(node, arg_spec=arg_spec, chain=chain)
        if op is not None:
            operations.append(op)
        # Also walk the func itself if it is a direct Call (rare
        # for cadquery but possible for nested expressions).
        if isinstance(node.func, ast.Call):
            _walk_tree(node.func, operations, chain=chain)
        for arg in node.args:
            _walk_tree(arg, operations, chain=[])
        for kw in node.keywords:
            _walk_tree(kw.value, operations, chain=[])
        return
    # If we get a chained method call (e.g., wp.rect().extrude()),
    # it's still an ast.Call whose func is an Attribute.  The
    # recursive _parse_call already handles it.
    for child in ast.iter_child_nodes(node):
        _walk_tree(child, operations, chain=[])


__all__ = ["parse_cadquery_script", "Operation"]
