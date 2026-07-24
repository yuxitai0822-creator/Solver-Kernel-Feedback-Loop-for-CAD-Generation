"""cad_agent/prompt_builder.py — Build the LLM CAD Agent prompt.

This module exposes a single ``build_prompt()`` function that is the
backward-compatible front door to the prompt system.

Behaviour
---------

* If ``feedback`` is ``None`` (the default), it renders the original
  Phase 2A prompt template — the same one the v0 single-shot
  ``p2b_full.py`` and the ZHIPU pilot use.  Existing call sites are
  untouched.

* If ``feedback`` is provided, it routes to
  ``cad_agent.prompt_builder_v2.build_prompt_v2()`` and renders the
  M0-M3 iterative prompt.  The ``feedback`` dict is forwarded as
  ``iter_history`` (the per-iteration verification records, already
  filtered by the caller to the method's exposed channels).

The two paths share the same output contract, so the agent backend
(``agent_v2.py``) does not need to know which path was taken.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Local v2 builder is one directory level away.
_v2_path = Path(__file__).resolve().parent
if str(_v2_path) not in sys.path:
    sys.path.insert(0, str(_v2_path))

from cad_agent.prompt_builder_v2 import (  # noqa: E402
    build_prompt_v2,
    DEFAULT_PERTURBATION_PLACEHOLDER,
)


# Original Phase 2A template — kept verbatim so the v0 prompt is
# byte-identical to what p2b_full.py and the ZHIPU pilot emitted.
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


def build_prompt(design_plan: dict | str,
                  current_script: str = "",
                  out_dir: str = "./out",
                  allowed_ops: list[str] | None = None,
                  feedback: list[dict] | None = None,
                  perturbation_description: str = DEFAULT_PERTURBATION_PLACEHOLDER,
                  iteration: int = 0,
                  max_iterations: int = 3) -> str:
    """Construct the LLM prompt.

    When ``feedback is None`` the original Phase 2A template is
    rendered (back-compat).  When ``feedback`` is a list, the
    M0-M3 iterative v2 template is rendered.  The two paths share
    the same output contract.

    Parameters
    ----------
    design_plan : dict | str
        Design plan (dict, or its JSON string form).
    current_script : str
        Most recent script (or empty for the first iteration).
    out_dir : str
        Per-iteration working directory.  The LLM is told to write
        to ``{out_dir}/generated.step`` exactly.
    allowed_ops : list[str] | None
        Op whitelist, or None for the full cadquery surface.
    feedback : list[dict] | None
        Per-iteration records from past iterations.  **Caller must
        pre-filter** by the active method's feedback channels.
    perturbation_description : str
        Free-form perturbation description.  Currently a placeholder
        — see TODO in ``prompt_builder_v2.py``.
    iteration : int
        0-indexed iteration counter.
    max_iterations : int
        Iteration cap.
    """
    if feedback is None:
        # ---- Phase 2A / v0 single-shot path. ----
        if isinstance(design_plan, dict):
            design_plan = json.dumps(design_plan, indent=2, ensure_ascii=False)
        if allowed_ops is None:
            allowed_ops_str = "(full cadquery surface)"
        else:
            allowed_ops_str = ", ".join(allowed_ops)
        return PROMPT_TEMPLATE.format(
            design_plan=design_plan,
            current_script=current_script or "(no prior script — generate from scratch)",
            out_dir=out_dir,
            out_step_path=str(Path(out_dir) / "generated.step"),
            allowed_ops=allowed_ops_str,
        )
    # ---- M0-M3 iterative path. ----
    return build_prompt_v2(
        design_plan=design_plan,
        previous_code=current_script,
        iter_history=feedback,
        perturbation_description=perturbation_description,
        allowed_ops=allowed_ops,
        out_dir=out_dir,
        iteration=iteration,
        max_iterations=max_iterations,
    )
