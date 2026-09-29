"""trace_builder.py — Build declared and executed operation traces.

Declared trace is built from the IR's operations list.
Executed trace is built from the adaptor's actual run results
(success / failure of each emitted statement).
"""
from __future__ import annotations

from typing import Any


def build_declared_trace(ir: dict) -> dict:
    """Return the declared operation trace."""
    return {
        "sample_id": ir.get("sample_id"),
        "trace_type": "declared",
        "operations": [
            {
                "op_id": op.get("op_id"),
                "op_type": op.get("op_type"),
                "role": op.get("role"),
                "input": op.get("input"),
                "params": op.get("params", {}),
                "status": "declared",
            }
            for op in ir.get("operations", [])
        ],
    }


def build_executed_trace(ir: dict,
                            execution_results: list[dict],
                            failed_at: str | None = None) -> dict:
    """Return the executed operation trace.

    execution_results: list of {op_id, op_type, status, error_type?, error_message?}
    """
    ops_out = []
    for r in execution_results:
        entry = {
            "op_id": r.get("op_id"),
            "op_type": r.get("op_type"),
            "runtime_status": r.get("status", "unknown"),
        }
        if r.get("error_type"):
            entry["error_type"] = r["error_type"]
        if r.get("error_message"):
            entry["error_message"] = r["error_message"]
        ops_out.append(entry)
    return {
        "sample_id": ir.get("sample_id"),
        "trace_type": "executed",
        "operations": ops_out,
        "failed_at": failed_at,
    }