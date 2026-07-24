"""cad_agent/prompt_builder_v2.py — M0-M3 iterative prompt builder.

Renders the prompt for one iteration of the M0-M3 agentic system.
The prompt has four content blocks:

    1.  System preamble (rules of engagement, output contract).
    2.  Design Plan.
    3.  Perturbation description (placeholder, see TODO below).
    4.  Previous code + filtered iter-history feedback.

The ``iter_history`` argument is a list of past iterations, each
already filtered to only include the verification channels the
active method exposes (see ``method_policy.METHOD_FEEDBACK_CHANNELS``).
The builder does no filtering itself; the caller is responsible for
the policy decision.

.. note::

    TODO (next phase): replace ``perturbation_description`` with the
    negative CAD code modality.  Per the user, perturbation today is
    a meta-label only — the LLM is given the *original* design plan
    and is expected to produce a STEP that matches the design plan.
    When the negative-cad-code modality is wired in, this slot will
    hold the perturbed history → perturbed script.
"""
from __future__ import annotations

import json
import textwrap
from typing import Any


# Default placeholder used when no perturbation description is
# available.  We deliberately do NOT load the perturbation meta into
# the prompt yet — the user has flagged this as the next phase.
DEFAULT_PERTURBATION_PLACEHOLDER = (
    "(perturbation description not yet wired — LLM is given the "
    "ORIGINAL design plan; see TODO in prompt_builder_v2.py)"
)


def _fmt_design_plan(plan: Any) -> str:
    """Pretty-print a design plan dict, or coerce a string."""
    if isinstance(plan, str):
        return plan
    return json.dumps(plan, indent=2, ensure_ascii=False)


def _fmt_previous_script(script: str) -> str:
    """Render the previous iteration's script (if any)."""
    s = (script or "").rstrip()
    if not s:
        return "(no prior script — generate from scratch)"
    return s


def _fmt_iter_history(iter_history: list[dict]) -> str:
    """Render the filtered iter-history as a multi-block string.

    Each entry is rendered with the verification results that the
    caller has chosen to expose.  Callers MUST pre-filter using
    ``method_policy.feedback_channels_for(method)``.

    An empty history renders as ``"(no prior iterations)"``.
    """
    if not iter_history:
        return "(no prior iterations)"

    blocks: list[str] = []
    for rec in iter_history:
        it = rec.get("iter", "?")
        blocks.append(f"--- iteration {it} ---")
        # Reasoning
        reason = rec.get("reasoning", "")
        if reason:
            blocks.append(f"  reasoning: {reason}")
        # Script
        scr = rec.get("script", "")
        if scr:
            blocks.append("  script:")
            blocks.append(textwrap.indent(scr, "    "))
        # Verification diagnostics (caller-filtered)
        verifs = rec.get("verifications") or {}
        exposed_channels = [c for c, v in verifs.items()
                            if isinstance(v, dict) and v.get("exposed")]
        if not exposed_channels:
            blocks.append("  feedback: (no feedback channels exposed for this method — "
                          "this iteration's verification failures are not visible to you; "
                          "self-correct from prior context)")
        else:
            for ch in exposed_channels:
                v = verifs.get(ch) or {}
                diag = v.get("diagnostic") or {}
                passed = v.get("passed", None)
                skipped = v.get("skipped", False)
                if skipped or passed is None:
                    blocks.append(f"  feedback.{ch}: (verification skipped — "
                                  f"reason: {v.get('skipped_reason', '?')})")
                    continue
                blocks.append(f"  feedback.{ch}: {'PASS' if passed else 'FAIL'}")
                blocks.append(textwrap.indent(json.dumps(diag, indent=2, ensure_ascii=False), "    "))
    return "\n".join(blocks)


def _fmt_allowed_ops(allowed_ops: list[str] | None) -> str:
    if not allowed_ops:
        return "(full cadquery surface)"
    return ", ".join(allowed_ops)


def build_prompt_v2(
    design_plan: Any,
    previous_code: str = "",
    iter_history: list[dict] | None = None,
    perturbation_description: str = DEFAULT_PERTURBATION_PLACEHOLDER,
    allowed_ops: list[str] | None = None,
    out_dir: str = "./out",
    iteration: int = 0,
    max_iterations: int = 3,
) -> str:
    """Render the M0-M3 iterative prompt.

    Parameters
    ----------
    design_plan : dict | str
        The original (unperturbed) design plan JSON.
    previous_code : str
        The current script (most recent iteration's ``script``), or
        empty on iteration 0.
    iter_history : list[dict] | None
        Per-iteration records from past iterations.  **Caller is
        responsible for filtering** by the active method's feedback
        channels; the builder does not filter.
    perturbation_description : str
        Free-form string describing the perturbation.  Currently a
        placeholder — see module docstring TODO.
    allowed_ops : list[str] | None
        Operation whitelist, or None for "full cadquery surface".
    out_dir : str
        Working directory (used to construct OUT_STEP_PATH).  In the
        M0-M3 system this is a per-iteration path; the prompt
        template embeds it because the LLM is told to write to
        OUT_STEP_PATH exactly.
    iteration : int
        0-indexed iteration counter (for the "Iteration N of K" line).
    max_iterations : int
        Iteration cap (echoed back to the LLM).
    """
    plan_str = _fmt_design_plan(design_plan)
    hist_str = _fmt_iter_history(iter_history or [])
    code_str = _fmt_previous_script(previous_code)
    ops_str = _fmt_allowed_ops(allowed_ops)
    out_step = f"{out_dir.rstrip('/')}/generated.step"

    return (
        "You are the CAD Generation Agent.\n"
        "\n"
        "Your task: produce a runnable cadquery Python script that "
        "realises the Design Plan below.  This is iteration "
        f"{iteration} of {max_iterations}.  Previous iterations "
        "(if any) are listed at the bottom of this prompt; their "
        "feedback has been filtered to the channels you are "
        "allowed to see.\n"
        "\n"
        "CRITICAL: your script MUST end with an explicit STEP export:\n"
        "  import cadquery as cq\n"
        "  ...  # build result\n"
        "  cq.exporters.export(result, OUT_STEP_PATH)\n"
        "\n"
        f"OUT_STEP_PATH is the absolute path {out_step}. Your script "
        "must write to it or the executor marks the run as failed.\n"
        "\n"
        "Output format (STRICT — must be valid JSON, no extra prose):\n"
        "{{\n"
        '  "action": "repair" | "no_change",\n'
        '  "script": "<full cadquery python source — must be runnable>",\n'
        '  "reasoning": "<one short paragraph: what you checked, what you changed, why>",\n'
        '  "operations_declared": ["rectangle", "extrude", ...],   // optional\n'
        '  "notes": "<one-line rationale>"                          // optional\n'
        "}}\n"
        "\n"
        "Rules:\n"
        "  1.  Action 'no_change' means the current script already "
        "matches the design plan — output only "
        "{\"action\": \"no_change\"}, no script field.\n"
        "  2.  Action 'repair' means emit a *complete* runnable "
        "cadquery script that replaces the current one.  Do NOT "
        "output an IR; do NOT output diff/patch; the script must "
        "run from a clean document.\n"
        "  3.  The script must use cadquery (= import cadquery as cq).\n"
        "  4.  All output paths should be under the directory given by OUT_DIR.\n"
        "  5.  Operate in millimeters.\n"
        "  6.  Reasoning is encouraged — it will help subsequent "
        "iterations (and the audit log) understand what you changed "
        "and why.\n"
        "\n"
        "Design Plan:\n"
        f"{plan_str}\n"
        "\n"
        "Perturbation description (TODO: replace with negative CAD code):\n"
        f"{perturbation_description}\n"
        "\n"
        "Previous CAD script (most recent iteration):\n"
        f"{code_str}\n"
        "\n"
        f"Previous iteration history (iteration {iteration}):\n"
        f"{hist_str}\n"
        "\n"
        f"Allowed operations: {ops_str}\n"
        f"OUT_DIR: {out_dir}\n"
        f"OUT_STEP_PATH: {out_step}\n"
    )


__all__ = [
    "build_prompt_v2",
    "DEFAULT_PERTURBATION_PLACEHOLDER",
]
