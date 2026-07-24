"""cad_agent/schema.py — Output contract for the LLM CAD Agent.

Phase 2A Task A1.3:  define the strict JSON contract for what the LLM
CAD Agent emits.  The Agent must produce a runnable cadquery script
(plus lightweight metadata); the script is fed to
``cad_runtime.executor.execute_cad_script`` and is parsed by
``code2oper`` for CED calculation.
"""
from __future__ import annotations

from typing import Any
import json


# Operation vocabulary the LLM MAY declare in `operations_declared`
# (which is optional).  This is informational only — the script
# itself is the source of truth and is parsed by code2oper.
# We accept cadquery's native API names ("rect", "circle", "extrude",
# etc.) AND the code2oper taxonomy names ("rectangle", "polygon",
# "shell", etc.) interchangeably, since the LLM may use either.
ALLOWED_OPERATIONS = {
    # code2oper taxonomy names
    "rectangle", "circle", "polygon", "arc",
    "extrude", "cut", "union", "shell", "fillet",
    "translate", "rotate", "mirror",
    # cadquery native API names
    "rect", "circle", "polyline", "polygon", "extrude", "cut",
    "union", "shell", "fillet", "chamfer", "translate", "rotate",
    "mirror", "line", "spline", "text", "workplane",
}


def is_valid_output(obj: dict) -> tuple[bool, str | None]:
    """Validate the Agent's output against the schema.

    Returns (is_valid, error_message_or_None).  The Agent may output
    a NO_CHANGE indicator (action: "no_change") to indicate it
    believes the current script already meets the design plan.

    For the M0-M3 iterative agentic system (Phase 2B), the LLM is
    asked to emit a ``reasoning`` field (free-form string) alongside
    the new code; this is OPTIONAL but if present must be a string
    no longer than 8 000 characters.  See
    ``cad_agent/prompt_builder_v2.py``.
    """
    if not isinstance(obj, dict):
        return False, f"output must be a dict, got {type(obj).__name__}"
    action = obj.get("action", "repair")
    if action not in ("repair", "no_change"):
        return False, f"action must be 'repair' or 'no_change', got {action!r}"
    if action == "repair":
        if "script" not in obj or not isinstance(obj["script"], str):
            return False, "script must be a string when action='repair'"
        # operations_declared is OPTIONAL; if present, validate loosely
        # against the union of cadquery + code2oper vocabulary.
        if "operations_declared" in obj:
            if not isinstance(obj["operations_declared"], list):
                return False, "operations_declared must be a list"
            for op in obj["operations_declared"]:
                if not isinstance(op, str) or len(op) > 60:
                    return False, f"operations_declared entries must be short strings; got {op!r}"
                # Permissive: any string op name accepted (cadquery has dozens of methods).
    if "reasoning" in obj and obj["reasoning"] is not None:
        if not isinstance(obj["reasoning"], str):
            return False, "reasoning must be a string"
        if len(obj["reasoning"]) > 8000:
            return False, f"reasoning too long ({len(obj['reasoning'])} > 8000 chars)"
    return True, None


def make_no_change(reason: str = "") -> dict:
    """Convenience for the Agent to indicate the current CAD is already
    correct (no repair needed).  Mirrors the IR-path NO_CHANGE flag."""
    return {"action": "no_change", "reason": reason}


def make_repair(script: str,
                operations_declared: list[str] | None = None,
                notes: str = "",
                reasoning: str = "") -> dict:
    """Convenience for the Agent to emit a full repair.

    Parameters
    ----------
    script : str
        Full runnable cadquery Python source.
    operations_declared : list[str] | None
        Optional list of op names (code2oper or cadquery native).
    notes : str
        Optional short one-line rationale.
    reasoning : str
        Optional free-form chain-of-thought for the M0-M3 iter loop.
    """
    obj: dict[str, Any] = {"action": "repair", "script": script}
    if operations_declared is not None:
        obj["operations_declared"] = list(operations_declared)
    if notes:
        obj["notes"] = notes
    if reasoning:
        obj["reasoning"] = reasoning
    return obj
