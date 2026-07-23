"""code2oper/parse.py — Public entry point for the AST-based parser.

Phase 2A Task A2.2.
"""
from __future__ import annotations

import json
import os
from typing import Any

from .ast_parser import parse_cadquery_script
from .taxonomy import Operation, param_to_dict


def parse_script_file(path: str) -> list[Operation] | None:
    """Parse a cadquery script on disk.  Returns None on parse
    failure, [] on empty, [...] on success."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return parse_cadquery_script(f.read())


def parse_to_json(path: str | None = None,
                   script: str | None = None) -> dict | None:
    """Convenience: return parse result as a JSON-serialisable dict
    (or None on parse failure)."""
    if path is not None:
        ops = parse_script_file(path)
    elif script is not None:
        ops = parse_cadquery_script(script)
    else:
        return None
    if ops is None:
        return None
    return {
        "n_operations": len(ops),
        "operations": [op.to_dict() for op in ops],
    }


__all__ = ["parse_cadquery_script", "parse_script_file", "parse_to_json",
           "Operation"]
