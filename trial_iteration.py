"""trial_iteration.py — One (method, sid, nid, layer) trial in the
M0-M3 iterative agentic system.

The per-trial loop is described in §4 of the M0-M3 spec.  Each
iteration:

    1.  Filter past-iteration feedback to the active method's
        exposed channels (per ``method_policy.METHOD_FEEDBACK_CHANNELS``).
    2.  Build the M0-M3 prompt (Design Plan + Previous Code + filtered
        iter_history + perturbation description).
    3.  Call the LLM agent (DeepSeek via ``agent_v2.call_cad_agent``).
    4.  Run all three Verification Objects (pipeline / solver / kernel).
    5.  If all three pass, return SUCCESS; if max_iter is hit, return
        FAILURE; otherwise record this iteration and continue.

The ``run()`` function is the only entry point used by
``p2b_iter_runner.py``.  It is also importable and testable.
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any

# Project-level imports.  We import inside ``run()`` (and the helpers
# below) rather than at module top so that ``trial_iteration`` can be
# imported by tools that don't have cadquery / OCP installed.
import sys

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import method_policy  # noqa: E402
import importlib.util as iu  # noqa: E402


def _load_agent_v2():
    """Load ``cad_agent/agent_v2.py`` as a module (it is not on the
    package's __init__.py)."""
    spec = iu.spec_from_file_location("agent_v2", str(_REPO_ROOT / "cad_agent" / "agent_v2.py"))
    m = iu.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


def _load_verification():
    """Load the cad_verification package."""
    from cad_verification import (  # noqa: WPS433
        PipelineVerification, SolverVerification, KernelVerification,
        VerificationResult,
    )
    return PipelineVerification, SolverVerification, KernelVerification, VerificationResult


# ---------------------------------------------------------------------------
# Plan / perturbation / history / KQP path resolvers
# ---------------------------------------------------------------------------
def _load_plan(sid: str) -> dict:
    p = _REPO_ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
    if not p.exists():
        p = _REPO_ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _load_perturbation(sid: str, nid: str) -> dict:
    p = (_REPO_ROOT / "task5_negative_perturbation" / "perturbations"
         / sid / nid / "perturbation_meta.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _find_history(sid: str) -> Path | None:
    p = _REPO_ROOT / "Reconstruction_results" / sid / "input_history.json"
    return p if p.exists() else None


def _find_kqp(sid: str) -> Path | None:
    p = _REPO_ROOT / "kqp" / "outputs" / "compiler_v0.2" / f"{sid}.kqp_instance.json"
    if p.exists():
        return p
    p = _REPO_ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sid}.kqp_instance.json"
    return p if p.exists() else None


def _perturbation_summary(meta: dict) -> str:
    """Render a one-line summary of the perturbation.

    This is the *placeholder* for the negative-CAD-code modality
    (see prompt_builder_v2.py TODO).  We only render the operator +
    original/perturbed values from the perturbation meta; the
    LLM is still given the *original* design plan.
    """
    if not meta:
        return ""
    op = meta.get("operator") or meta.get("operator_input_name") or "?"
    ov = meta.get("original_value", "?")
    pv = meta.get("perturbed_value", "?")
    return f"operator={op}; original={ov}; perturbed={pv} (see TODO: negative CAD code not yet wired)"


# ---------------------------------------------------------------------------
# Feedback filter — decouple "computed" from "exposed"
# ---------------------------------------------------------------------------
def _filter_iter_history(
    iter_records: list[dict],
    channels: set[str],
) -> list[dict]:
    """Project the per-trial iter_records to the active method's
    exposed feedback channels.

    The verification result for each iteration is retained; only the
    ``exposed`` flag changes per method.
    """
    out: list[dict] = []
    for r in iter_records:
        verifs = r.get("verifications") or {}
        projected: dict[str, Any] = {}
        for ch_name, ch_val in verifs.items():
            if not isinstance(ch_val, dict):
                projected[ch_name] = ch_val
                continue
            projected[ch_name] = {
                **ch_val,
                "exposed": ch_name in channels,
            }
        out.append({
            "iter":          r.get("iter"),
            "reasoning":     r.get("reasoning", ""),
            "script":        r.get("script", ""),
            "verifications": projected,
        })
    return out


def _format_verification(verif) -> dict[str, Any]:
    """Render a VerificationResult into the per-trial record shape.

    The ``exposed`` flag is filled in by ``_filter_iter_history`` on
    the next iteration; here we just project the VerificationResult.
    """
    if verif is None:
        return {"passed": None, "skipped": True, "diagnostic": {},
                "full": {}, "exposed": False}
    return {
        "passed":     verif.passed,
        "skipped":    verif.skipped,
        "diagnostic": verif.diagnostic,
        "full":       verif.full,
        "exposed":    False,  # filled by _filter_iter_history on next iter
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def run(
    method: str,
    sid: str,
    nid: str,
    layer: str,
    out_dir: Path | None = None,
    max_iterations: int | None = None,
) -> dict:
    """Run the M0-M3 iter loop for one trial.

    Returns a JSON-serialisable dict; the shape is the contract for
    ``p2b_iter_runner.py``.
    """
    if not method_policy.is_valid_method(method):
        raise ValueError(f"Unknown method {method!r}")

    max_iter = max_iterations or method_policy.MAX_ITERATIONS
    channels = method_policy.feedback_channels_for(method)

    plan        = _load_plan(sid)
    perturb     = _load_perturbation(sid, nid)
    perturb_str = _perturbation_summary(perturb)
    history_p   = _find_history(sid)
    kqp_p       = _find_kqp(sid)

    if out_dir is None:
        out_dir = _REPO_ROOT / "experiments" / "phase2b_iter" / method / sid / nid
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    agent_v2 = _load_agent_v2()
    PipelineVerification, SolverVerification, KernelVerification, VerificationResult = _load_verification()
    pipeline_v = PipelineVerification()
    solver_v   = SolverVerification()
    kernel_v   = KernelVerification()

    iter_records: list[dict] = []
    current_script = ""
    current_step_path: Path | None = None
    final_status = "failure"  # overwritten on success
    t0 = time.time()

    for it in range(max_iter):
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # 1. Filter feedback for the active method.
        filtered_history = _filter_iter_history(iter_records, channels)

        # 2. Call the LLM with the v2 prompt.
        try:
            obj = agent_v2.call_cad_agent(
                design_plan=plan,
                current_script=current_script,
                out_dir=str(iter_dir),
                feedback=filtered_history,
                perturbation_description=perturb_str,
                iteration=it,
                max_iterations=max_iter,
            )
        except Exception as e:  # noqa: BLE001
            # LLM call failed — record and abort.
            iter_records.append({
                "iter": it,
                "reasoning": "",
                "script": "",
                "verifications": {
                    "pipeline": _format_verification(None),
                    "solver":   _format_verification(None),
                    "kernel":   _format_verification(None),
                },
                "llm_error": f"{type(e).__name__}: {str(e)[:200]}",
            })
            final_status = "llm_error"
            break

        action = obj.get("action", "repair")
        if action == "no_change":
            # LLM self-declared success — exit early.  No script
            # produced; downstream verifications would have nothing
            # to test.
            iter_records.append({
                "iter": it,
                "reasoning": obj.get("reasoning", ""),
                "script": "",
                "agent_action": "no_change",
                "verifications": {
                    "pipeline": _format_verification(None),
                    "solver":   _format_verification(None),
                    "kernel":   _format_verification(None),
                },
            })
            final_status = "no_change"
            break

        new_script = obj.get("script", "")
        if not new_script:
            iter_records.append({
                "iter": it,
                "reasoning": obj.get("reasoning", ""),
                "script": "",
                "agent_action": "no_script",
                "verifications": {
                    "pipeline": _format_verification(None),
                    "solver":   _format_verification(None),
                    "kernel":   _format_verification(None),
                },
            })
            final_status = "no_script"
            break

        # 3. Run verifications IN SEQUENCE per spec §4:
        #    pipeline → solver → kernel
        # If a step fails, the downstream verifications are NOT
        # executed for this iteration.  We record each as a skipped
        # VerificationResult so the audit log still has the full
        # per-trial record; the LLM feedback filter then decides
        # whether to surface the failure (or absence) to the next
        # iteration's prompt.
        pipeline_res = pipeline_v.run(new_script, iter_dir)

        solver_res: VerificationResult | None = None
        if pipeline_res.passed is True and history_p is not None:
            solver_res = solver_v.run(history_p)
        else:
            # Solver skipped: either pipeline failed (no point solving
            # a sketch we won't use) or the history file is missing.
            skip_reason = "skipped: pipeline failed" \
                if pipeline_res.passed is not True else "skipped: history missing"
            solver_res = VerificationResult(
                name="solver",
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": skip_reason},
            )

        kernel_res: VerificationResult | None = None
        step_path_str = pipeline_res.full.get("step_path") if pipeline_res.passed else None
        if (pipeline_res.passed is True
                and solver_res is not None
                and solver_res.passed is True
                and step_path_str is not None
                and kqp_p is not None):
            kernel_res = kernel_v.run(Path(step_path_str), kqp_p, plan)
        else:
            # Kernel skipped: any upstream failure or missing artifact.
            reasons: list[str] = []
            if pipeline_res.passed is not True:
                reasons.append("pipeline failed")
            if solver_res is None or solver_res.passed is not True:
                reasons.append("solver did not pass")
            if kqp_p is None:
                reasons.append("kqp missing")
            kernel_res = VerificationResult(
                name="kernel",
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": "skipped: " + " & ".join(reasons) if reasons else "skipped"},
            )

        # 4. Record this iteration.
        iter_records.append({
            "iter": it,
            "reasoning": obj.get("reasoning", ""),
            "script": new_script,
            "verifications": {
                "pipeline": _format_verification(pipeline_res),
                "solver":   _format_verification(solver_res),
                "kernel":   _format_verification(kernel_res),
            },
        })

        # 5. Exit conditions.
        if (pipeline_res.passed is True
                and (solver_res is None or solver_res.passed is True)
                and (kernel_res is None or kernel_res.passed is True)):
            final_status = "success"
            current_step_path = (
                Path(pipeline_res.full["step_path"])
                if pipeline_res.full.get("step_path") else None
            )
            break

        # 6. Prepare for next iteration.
        current_script = new_script
        if it == max_iter - 1:
            final_status = "max_iter_exceeded"
            break

    return {
        "method": method,
        "sid": sid,
        "nid": nid,
        "layer": layer,
        "iterations": iter_records,
        "final_status": final_status,
        "n_iterations": len(iter_records),
        "feedback_channels_exposed": sorted(channels),
        "perturbation_summary": perturb_str,
        "history_path": str(history_p) if history_p else None,
        "kqp_path": str(kqp_p) if kqp_p else None,
        "wallclock": round(time.time() - t0, 2),
    }


__all__ = ["run"]
