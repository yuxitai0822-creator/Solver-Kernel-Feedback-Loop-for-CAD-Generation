"""cad_agent/prompt_builder.py — Build the generation prompt for the LLM CAD Agent.

Phase 2A Task A1.3.  The Agent receives a Design Plan and a current
CADScript (which may be empty for a fresh generation), and must emit
a strict JSON contract (see schema.py).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROMPT_TEMPLATE = """You are the CAD Generation Agent.

Your task: produce a runnable cadquery Python script that realises the
following Design Plan.  You have access to:
  - the Design Plan JSON
  - the current CAD script (may be empty if this is a fresh generation)
  - a list of allowed operations

CRITICAL: your script MUST end with an explicit STEP export:
  import cadquery as cq
  ...  # build result
  cq.exporters.export(result, OUT_STEP_PATH)

OUT_STEP_PATH is the absolute path. Your script must write to it or the executor marks the run as failed.

Output format (STRICT — must be valid JSON, no extra prose):

{{
  "action": "repair" | "no_change",
  "script": "<full cadquery python source — must be runnable>",
  "operations_declared": ["rectangle", "extrude", ...],   // optional
  "notes": "<one-line rationale>"                          // optional
}}

Rules:
  1.  Action "no_change" means the current script already matches the
     design plan — output only {{"action": "no_change"}}, no script field.
  2.  Action "repair" means emit a *complete* runnable cadquery script
     that replaces the current one.  Do NOT output an IR; do NOT output
     diff/patch; the script must run from a clean document.
  3.  The script must use cadquery (= import cadquery as cq).
  4.  All output paths should be under the directory given by OUT_DIR.
  5.  Operate in millimeters.

Design Plan:
{design_plan}

Current CAD script (may be empty):
{current_script}

Allowed operations: {allowed_ops}
OUT_DIR: {out_dir}
OUT_STEP_PATH: {out_dir}/generated.step
"""


def build_prompt(design_plan: dict | str, current_script: str = "",
                  out_dir: str = "./out",
                  allowed_ops: list[str] | None = None) -> str:
    """Construct the LLM generation prompt.

    Args:
        design_plan: Design Plan dict (or its JSON string form).
        current_script: current CAD script (may be empty).
        out_dir: where the LLM's script should write its output.
        allowed_ops: list of allowed cadquery operations.  If None,
            the LLM is told it has access to the full cadquery surface.
    """
    if isinstance(design_plan, dict):
        design_plan = json.dumps(design_plan, indent=2, ensure_ascii=False)
    if allowed_ops is None:
        allowed_ops_str = "(full cadquery surface)"
    else:
        allowed_ops_str = ", ".join(allowed_ops)
    return PROMPT_TEMPLATE.format(
        design_plan=design_plan,
        current_script=current_script or "(no prior script — generate from scratch)",
        out_dir=out_dir, out_step_path=str(Path(out_dir) / "generated.step"),
        allowed_ops=allowed_ops_str,
    )
