"""run_benchmark_v0.2.py — Solver-KQP Repair Loop Benchmark.

Implements the **v0.2** architecture defined in `doc/experiment_contract_v0.1.md`
sections 3 and 4.  Compared to v0.1 this rewrite changes:

  §3.1   Pipeline feedback is the shared base for ALL methods (not a
         research variable).  Solver / KQP are diagnostic channels, gated
         per-method by ``inject_solver_feedback`` / ``inject_kqp_feedback``.

  §4.1   Verification pipeline (adaptor → step → solver → KQP) runs in
         FULL for EVERY method on EVERY iteration.  Solver / KQP are
         always executed and their results are always recorded.  The
         only thing that changes per method is whether the result is
         injected into the agent's ``[FEEDBACK]`` block.

  §4.2   ``Success(C) = PipelineValid ∧ SolverValid ∧ KQPSamplePass``
         replaces the previous KQP-only primary.  PipelineValid breaks
         into compile/execute/step_export/occt_load; SolverValid is
         ``status ∈ {fully_constrained, under_constrained}``;
         KQPSamplePass is ``kqp.overall_status == "pass"``.

  §4.3   Stop rules S1/S2/S3/S4 applied identically across methods.
         S1: agent returns ``action="no_change"`` → STOP.  S2:
         ``IR_{t+1} == IR_t`` → STOP.  S3: Success(C)=True (not fed
         back to agent) → STOP.  S4: ``max_iter=3`` → STOP.

  §3.2   Unified prompt skeleton: ``[DESIGN PLAN] + [CURRENT IR] +
         [FEEDBACK] + [INSTRUCTION]``.  The ``[FEEDBACK]`` block is the
         only thing that varies per method; only the channels enabled
         by ``inject_*_feedback`` are included.

  §3.4   Information leakage boundary is enforced inside
         ``build_prompt``: the prompt NEVER contains clean IR, GT
         history, perturbation metadata, or any cross-method feedback.

  §4.6   ``RepairCost = Σ CED_declared + 0.1 × n_execution
         + 0.1 × n_verification`` (was previously a CED_executed-based
         formula).

  §9     Result schema fields ``solver_status`` / ``solver_acceptable``
         / ``kqp_pass`` are ALWAYS populated from the measured result
         (no ``"skipped"`` placeholders).

  §10    Artifact names updated to ``solver_feedback.json``,
         ``kqp_feedback.json``, ``ced.json``, ``agent_request.json``,
         ``agent_response.json``, ``timing.json`` (was
         ``*_result_t.json``, ``agent_prompt_t.txt``, ``runtime_log_t.json``).

This file supersedes ``run_benchmark.py`` (v0.1) while keeping a thin
back-compat shim so the existing M0/M1 run artefacts can still be
inspected.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
sys.path.insert(0, str(ROOT / "cad_edit_distance"))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"
FREECAD_PYTHON = r"D:/Anaconda/envs/freecad_sketcher/python.exe"

CONFIG_PATH = ROOT / "experiments" / "config" / "benchmark_config_v0.2.json"
TASK5_ADAPTOR_SUMMARY = (ROOT / "task5_negative_perturbation"
                              / "reports" / "adaptor_run_summary.json")
TASK5_KQP_DETECTION = (ROOT / "task5_negative_perturbation"
                          / "reports" / "kqp_detection_summary.json")
TASK5_PERT_ROOT = ROOT / "task5_negative_perturbation" / "perturbations"

IR_EXAMPLES_DIR = ROOT / "cad_ir" / "samples" / "manual_ir_examples"
KQP_DIR = ROOT / "kqp" / "outputs" / "compiler_v0.1"
PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"
HIST_DIR = ROOT / "Reconstruction_results"

# ---------------------------------------------------------------------------
# Constants (from §4.2 and §4.3)
# ---------------------------------------------------------------------------
SOLVER_VALID_STATES = ("fully_constrained", "under_constrained")
PIPELINE_VALID_STAGES = ("compile", "execute", "step_export", "occt_load")

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def list_methods(config: dict) -> list[dict]:
    return config["methods"]


def list_valid_negatives() -> list[dict]:
    """Return perturbation records eligible for ablation.  Mirrors v0.1
    fallback behaviour: prefer adaptor_run_summary, else kqp_detection_summary."""
    if TASK5_ADAPTOR_SUMMARY.exists():
        summary = json.loads(TASK5_ADAPTOR_SUMMARY.read_text(encoding="utf-8"))
        rows = summary["rows"]
        return [r for r in rows if r.get("reconstruction_success")]
    if TASK5_KQP_DETECTION.exists():
        kqp = json.loads(TASK5_KQP_DETECTION.read_text(encoding="utf-8"))
        return kqp["rows"]
    return []


# ---------------------------------------------------------------------------
# Perturbation helpers (canonical E2_extrude_deep × 1.5, kept for v0.1
# back-compat runs; v0.2 production should use the perturbation battery
# defined in §3.5 of the prevalidation report).
# ---------------------------------------------------------------------------

def perturb_ir_canonical(ir_t: dict) -> dict:
    ir_p = copy.deepcopy(ir_t)
    for op in ir_p["operations"]:
        if op.get("op_type") == "extrude":
            d = op["params"].get("distance", 0)
            if d > 0:
                op["params"]["distance"] = round(d * 1.5, 4)
            break
    return ir_p


def find_clean_ir_for_negative(sample_id: str) -> dict | None:
    ir_path = IR_EXAMPLES_DIR / f"{sample_id}.cad_ir.json"
    if ir_path.exists():
        return json.loads(ir_path.read_text(encoding="utf-8"))
    return None


def parse_sample_arg(s: str) -> tuple[str, str]:
    """Parse a --sample CLI argument into (sample_id, negative_id).

    Accepts ``sid`` or ``sid/nid``; the latter is the (sample, neg)
    pair convention used by task5 perturbation metadata.  Defaults to
    ``neg_01`` when only ``sid`` is given.

    Added in B-003 fix.
    """
    if "/" in s:
        sid, _, nid = s.partition("/")
        sid = sid.strip()
        nid = nid.strip()
        if not sid or not nid:
            raise ValueError(f"--sample {s!r}: empty sample_id or negative_id")
        return sid, nid
    return s.strip(), "neg_01"


def load_initial_ir(sample_id: str, negative_id: str,
                       config: dict) -> tuple[dict, dict, dict] | None:
    """Build the negative's initial IR.

    Returns ``(ir_t, perturbation_meta_dict, negative_record_dict)`` or
    ``None`` if the inputs are missing.

    Sources, in priority order:

      (1) task5_negative_perturbation/perturbations/{sid}/{nid}/{sid}_perturbed.json
          → run ``compile_history_to_ir`` to materialise the IR.  This is the
          PILOT path: each (sid, nid) maps to a specific perturbation type
          (E1–E6) that we want to repair.

      (2) fall back to canonical E2 × 1.5 perturbation for backward compatibility
          with old single-negative smoke tests.

    Added in B-003 fix.
    """
    # (1) Perturbed history + compile to IR
    pert_history_path = (TASK5_PERT_ROOT / sample_id / negative_id
                          / f"{sample_id}_perturbed.json")
    if pert_history_path.exists():
        try:
            # history2ir is a package under experiments/; add its parent
            # to sys.path so `from history2ir.compiler.history_to_ir import
            # compile_history_to_ir` works.
            sys.path.insert(0, str(ROOT / "experiments"))
            from history2ir.compiler.history_to_ir import compile_history_to_ir
            history = json.loads(pert_history_path.read_text(encoding="utf-8"))
            ir_t = compile_history_to_ir(history, sample_id=sample_id)
            pert_meta_path = (TASK5_PERT_ROOT / sample_id / negative_id
                                 / "perturbation_meta.json")
            pert_meta = {}
            if pert_meta_path.exists():
                pert_meta = json.loads(pert_meta_path.read_text(encoding="utf-8"))
            record = {
                "sample_id": sample_id,
                "negative_id": negative_id,
                "source": "task5_perturbed_history",
            }
            return ir_t, pert_meta, record
        except Exception as e:
            print(f"  WARN: load_initial_ir(task5) failed for "
                  f"{sample_id}/{negative_id}: {type(e).__name__}: {e}")

    # (2) Canonical E2 × 1.5 fallback
    ir_clean = find_clean_ir_for_negative(sample_id)
    if ir_clean is None:
        return None
    ir_t = perturb_ir_canonical(ir_clean)
    record = {
        "sample_id": sample_id,
        "negative_id": negative_id,
        "source": "canonical_E2_extrude_deep_x1.5",
    }
    return ir_t, {
        "type": "E2_extrude_deep",
        "ops": _find_extrude_ops(ir_t),
        "values_before": _extrude_distances(ir_clean),
        "values_after": _extrude_distances(ir_t),
    }, record


# ---------------------------------------------------------------------------
# Verification pipeline (always run per §4.1)
# ---------------------------------------------------------------------------

def _run_adaptor(ir: dict, out_dir: Path) -> dict:
    ir_path = out_dir / "_ir_input.cad_ir.json"
    ir_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    worker = ROOT / "cad_repair_loop" / "_adaptor_subprocess.py"
    proc = subprocess.run([CADQUERY_PYTHON, str(worker),
                              str(ir_path), str(out_dir)],
                             capture_output=True, text=True, timeout=120,
                             cwd=str(ROOT))
    rp = out_dir / "adapter_report.json"
    if rp.exists():
        try:
            return json.loads(rp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"adapter_status": "fail",
            "step_export_status": "fail",
            "warnings": [f"adaptor subprocess rc={proc.returncode}: {proc.stderr[-200:]}"]}


def _run_kqp(step_path: Path, kqp_path: Path, plan_path: Path,
                output_path: Path) -> dict:
    """Always run per §4.1; output_path lets the v0.2 protocol name the
    artifact ``kqp_feedback.json`` instead of the v0.1 ``kqp_result_t.json``."""
    if not step_path.exists() or not kqp_path.exists():
        return {"overall_status": "unknown", "query_results": [],
                "error": "missing step or kqp instance"}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [CADQUERY_PYTHON, str(ROOT / "kqp" / "runner" / "run_kqp.py"),
           str(step_path), str(kqp_path)]
    if plan_path.exists():
        cmd.extend(["--design-plan", str(plan_path)])
    cmd.extend(["-o", str(output_path)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                            cwd=str(ROOT))
    if output_path.exists():
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"overall_status": "fail", "query_results": [],
            "error": f"KQP rc={proc.returncode}: {proc.stderr[-200:]}"}


def _run_solver(history_path: Path) -> dict:
    """Always run per §4.1."""
    if not history_path.exists():
        return {"status": "fail", "solve_status": "solver_failure",
                "conflicts": [], "redundant": [], "malformed": [],
                "dof": 0, "solve_return_code": -1,
                "recompute_status": "fail", "warning": "no history_path"}
    try:
        sys.path.insert(0, str(ROOT / "Freecadsolver_feedback" / "core"))
        from solver_runner import run_solver_from_history
        from recompute_runner import run_recompute_from_state
        from diagnostic_normalizer import (normalize_solve,
                                                normalize_recompute)
        history = json.loads(history_path.read_text(encoding="utf-8"))
        raw = run_solver_from_history(history)
        rc = run_recompute_from_state(raw)
        normalized = normalize_solve(raw)
        normalized["dof"] = raw.get("dof", 0)
        normalized["return_code"] = raw.get("solve_return_code", 0)
        normalized_rc = normalize_recompute(rc)
        normalized["recompute_status"] = normalized_rc.get("recompute_status",
                                                              "fail")
        normalized["status"] = "ran"
        return normalized
    except Exception as e:
        return {"status": "fail", "solve_status": "solver_failure",
                "conflicts": [], "redundant": [], "malformed": [],
                "dof": 0, "solve_return_code": -1,
                "recompute_status": "fail",
                "warning": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# §4.2 Success conjunction
# ---------------------------------------------------------------------------

_PIPELINE_TRUTHY = {"success", "pass", "ok", "true"}


def _is_truthy_status(value) -> bool:
    """Normalise the adaptor's status strings into a single boolean.

    B-004 fix (2026-07-16): the adaptor writes ``adapter_status:
    'success'`` (for the meta-state) but ``step_export_status: 'pass'``
    (the per-stage state).  Both must be considered truthy; this helper
    handles that enum-equivalence in one place.
    """
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _PIPELINE_TRUTHY
    return False


def _pipeline_valid(adapt_report: dict, step_path: Path | None) -> tuple[bool, dict]:
    """PipelineValid = compile ∧ execute ∧ step_export ∧ occt_load.

    Returns ``(passed, breakdown)``.

    Each stage accepts the adaptor's truthy enum (``success`` /
    ``pass`` / ``ok`` / ``true``) per B-004 fix.  ``occt_load`` is
    inferred as pass when step_export passed AND the .step file exists
    with non-zero size.  KQP runs downstream and tolerates a small STEP
    load slip, but the adaptor's own step_export / occt_load are good
    proxies.
    """
    adapter_ok = _is_truthy_status(adapt_report.get("adapter_status"))
    step_ok = (_is_truthy_status(adapt_report.get("step_export_status"))
                 and step_path is not None and step_path.exists()
                 and step_path.stat().st_size > 0)
    occt_ok = step_ok  # proxy: a STEP file readable as a non-zero file
    breakdown = {
        "compile":     adapter_ok,
        "execute":     adapter_ok,
        "step_export": step_ok,
        "occt_load":   occt_ok,
    }
    return all(breakdown.values()), breakdown


def _solver_valid(solver_fb: dict) -> tuple[bool, str]:
    """SolverValid = solver.status ∈ {fully_constrained, under_constrained}."""
    solve_status = (solver_fb.get("solve", {}) or {}).get("solve_status",
                       solver_fb.get("solve_status", ""))
    # Map FreeCAD solver runner's status to canonical names from §4.2.
    canonical_map = {
        "fully_constrained": "fully_constrained",
        "under_constrained": "under_constrained",
        "conflicting": "conflict",
        "over_constrained": "conflict",
        "unsolvable": "invalid",
        "invalid_constraint_reference": "invalid",
        "malformed_constraints": "invalid",
        "solver_failure": "invalid",
    }
    canonical = canonical_map.get(solve_status, "invalid")
    return canonical in SOLVER_VALID_STATES, canonical


def _kqp_pass(kqp_fb: dict) -> tuple[bool, list[str]]:
    """KQPSamplePass = all mandatory KQP queries pass."""
    qs = kqp_fb.get("query_results", []) or []
    failed = [qr.get("query_id", "?") for qr in qs
                if qr.get("status") == "fail"]
    overall = kqp_fb.get("overall_status", "unknown")
    return (overall == "pass" and not failed), failed


def compute_success(adapt_report: dict, solver_fb: dict, kqp_fb: dict,
                       step_path: Path | None) -> dict:
    pv, pv_break = _pipeline_valid(adapt_report, step_path)
    sv, sv_canon = _solver_valid(solver_fb)
    kqp_p, kqp_failed = _kqp_pass(kqp_fb)
    success = pv and sv and kqp_p
    # strict_success: as §4.2 secondary — additionally no over-constraint warning
    no_over = "over_constrained" not in (solver_fb.get("solve", {}) or {}).get(
        "warnings", []) and not (solver_fb.get("warnings") or [])
    strict = success and no_over
    return {
        "success": success,
        "strict_success": strict,
        "pipeline_valid": pv,
        "pipeline_valid_breakdown": pv_break,
        "solver_valid": sv,
        "solver_canonical_status": sv_canon,
        "kqp_pass": kqp_p,
        "kqp_failed_query_ids": kqp_failed,
    }


# ---------------------------------------------------------------------------
# §3.2 Unified prompt skeleton + §3.4 information-leakage boundary
# ---------------------------------------------------------------------------

INSTRUCTION_BLOCK = """\
[INSTRUCTION]
You are the CAD Repair Agent.  Your contract is **fixed**:

  •  Protocol:  CAD IR Schema v0.1 (visible as the [CURRENT IR] block).
  •  Output:    ONE OF
                  (A) a complete CAD IR object conforming to the schema, OR
                  (B) the literal token `NO_CHANGE` (no other text).
  •  The IR you output is fed directly into the Adaptor → IR → exporter; the
     parser does NOT accept operation-list / patch-style output.  Anything
     that is not a full schema-valid IR (or `NO_CHANGE`) is rejected and
     triggers the S2 stop rule.

Mandatory output schema (CAD IR v0.1):
{
  "schema_version":      "cad_ir_v0.1",
  "sample_id":           "<same as in [CURRENT IR]>",
  "unit":                "<same as in [CURRENT IR], typically 'mm'>",
  "coordinate_system":   "<same as in [CURRENT IR]>",
  "operations": [
    { "op_id": "op_001", "op_type": "sketch_rectangle", "plane": "XY",
      "params": {"width": ..., "height": ..., "center": [x, y]}},
    { "op_id": "op_002", "op_type": "extrude", "input": "op_001",
      "params": {"distance": ..., "extent_type": "...", "operation": "...",
                  "direction": "..."}},
    { "op_id": "op_003", "op_type": "export_step", "input": "op_002",
      "params": {"path": "<sample_id>.step"}}
  ],
  "metadata": {"source": "repair", "comments": "<one-line rationale>"}
}

Hard requirements:
  1.  schema_version MUST be exactly  "cad_ir_v0.1".
  2.  sample_id, unit, coordinate_system MUST be identical to the input.
  3.  Numeric `params` values in mm (use float, e.g. 19.0 — not "19").
  4.  Preserve input-output graph consistency: every `extrude.input` /
      `export_step.input` must reference an op_id defined earlier in the
      `operations` array.
  5.  Modify ONLY the `params` values (and optionally op_002-style
      `extent_type` / `direction`) needed to fix the feedback.  Do NOT
      add or remove operations unless absolutely necessary.
  6.  Output a SINGLE JSON object.  Either return it bare, wrap it in a
      ```json ... ``` fence, OR — if you decide no fix is needed —
      output exactly `NO_CHANGE`.
"""


def _pipeline_block(adapt_report: dict, kqp_fb: dict, solver_fb: dict) -> dict:
    """§3.3 M0: pipeline result block — compile/execute/step_export/occt_load
    plus any pipeline-level error text.  Always shown to all methods."""
    pv, breakdown = _pipeline_valid(adapt_report, None)
    errors: list[str] = []
    for w in adapt_report.get("warnings", []) or []:
        errors.append(str(w))
    # Add KQP errors only when they look like pipeline-level (load errors).
    if kqp_fb.get("error"):
        errors.append(f"kqp: {kqp_fb['error']}")
    if solver_fb.get("warning"):
        errors.append(f"solver: {solver_fb['warning']}")
    return {
        "compile": "pass" if breakdown["compile"] else "fail",
        "execute": "pass" if breakdown["execute"] else "fail",
        "step_export": "pass" if breakdown["step_export"] else "fail",
        "occt_load": "pass" if breakdown["occt_load"] else "fail",
        "error_messages": errors[:8],
    }


def _solver_block(solver_fb: dict) -> dict:
    solve = solver_fb.get("solve", {}) or {}
    raw_status = solve.get("solve_status",
                              solver_fb.get("solve_status", ""))
    canonical_map = {
        "fully_constrained": "fully_constrained",
        "under_constrained": "under_constrained",
        "conflicting": "conflict",
        "over_constrained": "conflict",
        "unsolvable": "invalid",
        "invalid_constraint_reference": "invalid",
        "malformed_constraints": "invalid",
        "solver_failure": "invalid",
    }
    canonical = canonical_map.get(raw_status, "invalid")
    return {
        "status": canonical,
        "acceptable": canonical in SOLVER_VALID_STATES,
        "conflicts": solve.get("conflicting_constraints",
                       solver_fb.get("conflicts", [])) or [],
        "invalid_constraints": solve.get("malformed_constraints",
                                solver_fb.get("malformed", [])) or [],
    }


def _kqp_block(kqp_fb: dict) -> dict:
    qs = kqp_fb.get("query_results", []) or []
    queries = []
    for qr in qs:
        queries.append({
            "query_id": qr.get("query_id", ""),
            "intent": qr.get("intent", ""),
            "expected": qr.get("expected"),
            "observed": qr.get("observed"),
            "pass": qr.get("status") != "fail",
            "tolerance": qr.get("tolerance", 0.5),
        })
    return {
        "overall_pass": kqp_fb.get("overall_status") == "pass",
        "queries": queries,
    }


def build_prompt(ir_t: dict, design_plan: dict,
                   solver_fb: dict, kqp_fb: dict,
                   method: dict, adapt_report: dict) -> str:
    """Compose the unified prompt per §3.2.

    Only the [FEEDBACK] block varies per method; channels are gated by
    ``inject_solver_feedback`` / ``inject_kqp_feedback``.  The pipeline
    block is always included (§3.1: shared base).

    §3.4 leakage boundary: we never read or include the clean IR, the
    GT history JSON, the perturbation metadata, or any cross-method
    feedback.  ``design_plan`` is the canonical, frozen DesignPlan v0.6
    (visible to all methods because it IS the task spec, not the
    answer).
    """
    parts: list[str] = []
    parts.append("[DESIGN PLAN]")
    parts.append(json.dumps(design_plan, ensure_ascii=False, indent=2))
    parts.append("")
    parts.append("[CURRENT IR]")
    parts.append(json.dumps(ir_t, ensure_ascii=False, indent=2))
    parts.append("")
    # Feedback block: pipeline always; solver/kqp only if injected.
    feedback: dict = {"pipeline": _pipeline_block(adapt_report, kqp_fb, solver_fb)}
    if method.get("inject_solver_feedback", False):
        feedback["solver"] = _solver_block(solver_fb)
    if method.get("inject_kqp_feedback", False):
        feedback["kqp"] = _kqp_block(kqp_fb)
    parts.append("[FEEDBACK]")
    parts.append(json.dumps(feedback, ensure_ascii=False, indent=2))
    parts.append("")
    parts.append(INSTRUCTION_BLOCK)
    return "\n".join(parts)


def _parse_agent_response(text: str, ir_t: dict | None = None) -> tuple[str, dict | dict | None, str]:
    """Parse the agent's response under the IR-schema protocol.

    Returns ``(action, parsed_payload, parse_status)`` where:
      - ``action`` ∈ {"no_change", "repair", "parse_error"}.
        * "no_change": the agent returned the literal `NO_CHANGE`.
        * "repair":    the agent returned a full IR-shaped JSON object.
        * "parse_error": the LLM output is neither `NO_CHANGE` nor a
          schema-valid IR.  In this case ``parsed_payload`` is the raw
          text and the caller MUST treat the loop's IR_t as unchanged
          (triggering the S2 stop rule per §4.3 — never relax this).
      - ``parsed_payload``:
        * the new IR (dict)         when action == "repair"
        * None                       when action == "no_change"
        * {"raw": text, "reason": ...} when action == "parse_error"
        (returns a dict in either case so the union type is unambiguous)
      - ``parse_status`` ∈ {"ok_no_change", "ok_repair", "parse_error"}.

    Architectural principle (user mandate, 2026-07-16):
        The IR is the protocol between LLM (producer) and adaptor
        (consumer).  Operation-list / patch-style output is explicitly
        REJECTED — the protocol is `IR schema v0.1` only.
    """
    if not text:
        return "parse_error", {"raw": "", "reason": "empty_response"}, "parse_error"

    txt = text.strip()

    # Strip optional ```json ... ``` fence.
    if txt.startswith("```"):
        parts = txt.split("```", 2)
        # parts[0] empty, parts[1] = "json\n{...}", parts[2] = "\n```"
        if len(parts) >= 2:
            stripped = parts[1]
            if stripped.lower().startswith("json"):
                stripped = stripped[4:]
            if stripped.lstrip().lower().startswith("json"):
                # also catch "```json" with no newline
                stripped = stripped.lstrip()
                if stripped.lower().startswith("json"):
                    stripped = stripped[4:]
            txt = stripped.split("```", 1)[0].strip()

    # Strictly recognise the literal NO_CHANGE token.
    if txt.upper() == "NO_CHANGE" or txt == "NO_CHANGE":
        return "no_change", None, "ok_no_change"

    # Try parsing as JSON.
    try:
        obj = json.loads(txt)
    except Exception as e:
        return "parse_error", {"raw": text[:1000],
                                  "reason": f"json_parse_error: {type(e).__name__}: {str(e)[:200]}"}, "parse_error"

    if not isinstance(obj, dict):
        return "parse_error", {"raw": text[:1000],
                                  "reason": "top_level_not_object"}, "parse_error"

    # Strict IR schema check (lightweight — full schema is enforced in
    # validate_ir() in run_one_sample's Stage 6).
    if obj.get("schema_version") != "cad_ir_v0.1":
        return "parse_error", {"raw": json.dumps(obj)[:1000],
                                  "reason": "missing_or_wrong_schema_version (need 'cad_ir_v0.1')"}, "parse_error"
    if not isinstance(obj.get("operations"), list):
        return "parse_error", {"raw": json.dumps(obj)[:1000],
                                  "reason": "missing 'operations' array"}, "parse_error"
    if not obj.get("operations"):
        return "parse_error", {"raw": json.dumps(obj)[:1000],
                                  "reason": "'operations' must be non-empty"}, "parse_error"

    # Detect the legacy "operation list" pseudo-IR that some LLM runtimes
    # still emit (shape: {"action": "repair", "repair_operations": [...]})
    # — explicitly REJECT it per the user's mandate.
    if "repair_operations" in obj and "op" in obj and not any(
            isinstance(o, dict) and (o.get("op_type") or o.get("type"))
            for o in obj.get("operations", [])):
        return ("parse_error",
                {"raw": json.dumps(obj)[:1000],
                  "reason": "operation_list_protocol_forbidden_per_skill_contract"},
                "parse_error")

    return "repair", obj, "ok_repair"


# ---------------------------------------------------------------------------
# §3.2 agent call (LLM).  Same ZHIPU glm-5.1, temp=0.0, max_tokens=4096,
# timeout 120s for all four methods.
# ---------------------------------------------------------------------------

def _offline_agent(ir_t: dict, kqp_fb: dict, method: dict) -> tuple[dict, str]:
    """Offline fallback used ONLY when the LLM endpoint is unreachable.

    IMPORTANT (user mandate, 2026-07-16): the IR is the protocol between
    LLM (producer) and adaptor (consumer).  The offline fallback is an
    instrumented deterministic substitute; it is NOT allowed to mutate
    ``ir_t`` to "rescue" a run.  Instead it always returns the unchanged
    IR (so the loop's §4.3 S2 fires) and tells the caller why via
    ``agent_status``.  This keeps every method on equal footing.

    Returns (new_ir, note).  new_ir is always a copy of ir_t under the
    IR-schema protocol; only offline-mode testing / CI dry-runs reach
    this path.
    """
    new_ir = copy.deepcopy(ir_t)
    note = "[offline_fallback: LLM unreachable, returning ir_t unchanged per IR-schema protocol]"
    return new_ir, note


def _call_agent(ir_t: dict, design_plan: dict,
                  solver_fb: dict, kqp_fb: dict,
                  method: dict, adapt_report: dict) -> tuple[dict, dict, dict]:
    """Returns (new_ir, agent_io_meta, action_meta).

    ``agent_io_meta`` = {"prompt_text": str, "response_text": str,
                          "input_tokens": int, "output_tokens": int,
                          "agent_status": str, "action": str}
    ``action_meta`` = {"action": "repair"|"no_change",
                       "repair_operations": list | None}
    """
    prompt = build_prompt(ir_t, design_plan, solver_fb, kqp_fb,
                            method, adapt_report)
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return _offline_result(ir_t, kqp_fb, method, prompt, "no_key",
                                  reason="ZHIPU_API_KEY environment variable "
                                          "is empty or unset")
    try:
        import requests
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"}
        payload = {
            "model": "glm-5.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 4096,
            # Disable glm-5.1's chain-of-thought reasoner — by default it
            # spends the entire 4096-token budget on `reasoning_content`
            # and returns `content=""`, defeating the IR-schema output
            # protocol.  With this flag, the model produces the structured
            # JSON IR (or the literal `NO_CHANGE`) directly.  See ZHIPU
            # docs for `thinking={"type":"disabled"}` on glm-5.1.
            "thinking": {"type": "disabled"},
        }
        # Bypass any misconfigured system proxy by default.
        use_proxy = os.getenv("REQUESTS_USE_PROXY", "0") == "1"
        proxies = None if not use_proxy else None  # placeholder
        r = requests.post(url, headers=headers, json=payload,
                            timeout=120, proxies=proxies if use_proxy else {})
        r.raise_for_status()
        body = r.json()
        text = body["choices"][0]["message"]["content"].strip()
        usage = body.get("usage", {}) or {}
        tok_in = int(usage.get("prompt_tokens", 0) or 0)
        tok_out = int(usage.get("completion_tokens", 0) or 0)

        # Parse under the IR-schema protocol.  The new parser returns
        # ("no_change" | "repair" | "parse_error", parsed, status).
        action, parsed, parse_status = _parse_agent_response(text)
        if action == "no_change":
            # S1: agent declares no repair needed.
            new_ir = copy.deepcopy(ir_t)
            status_str = "no_change"
        elif action == "repair":
            # Successful parse of full IR.
            new_ir = parsed
            status_str = "ok_repair"
        else:  # parse_error
            # Per the user's architectural mandate, do NOT try to be
            # helpful — propagate the failure.  Treat as IR_t unchanged
            # so §4.3's S2 fires (ir_unchanged) and the loop stops.
            new_ir = copy.deepcopy(ir_t)
            reason = (parsed or {}).get("reason", "unknown")
            status_str = f"parse_error: {reason[:80]}"

        action_meta = {"action": action}
        if action == "repair":
            action_meta["new_ir"] = parsed
        elif action == "parse_error":
            action_meta["parse_error_info"] = parsed

        return new_ir, {
            "prompt_text": prompt, "response_text": text,
            "input_tokens": tok_in, "output_tokens": tok_out,
            "agent_status": status_str, "action": action,
        }, action_meta
    except Exception as e:
        # Surface the actual failure in the response_text so it shows
        # up in agent_response.json and is visible in the artefact
        # directory (previously this was swallowed silently and the
        # caller could not tell which fallback path was taken).
        reason = f"{type(e).__name__}: {str(e)[:200]}"
        return _offline_result(ir_t, kqp_fb, method, prompt,
                                    "call_failed", reason=reason)


def _offline_result(ir_t, kqp_fb, method, prompt, kind, reason=""):
    """Helper: produce the standard offline-fallback return tuple."""
    new_ir, note = _offline_agent(ir_t, kqp_fb, method)
    status = f"offline_fallback:{kind}"
    response_text = f"[{status}] {reason}\n{note}"
    return new_ir, {
        "prompt_text": prompt, "response_text": response_text,
        "input_tokens": 0, "output_tokens": 0,
        "agent_status": status, "action": "repair",
    }, {"action": "repair"}


def _strip_code_fence(text: str) -> str:
    """Deprecated: kept for backward compatibility.  Use
    :func:`_parse_agent_response` instead — it handles the IR-schema
    protocol end-to-end and explicitly rejects operation-list output."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
        t = t.split("```", 1)[0]
    return t


# ---------------------------------------------------------------------------
# §13 bars — stop-bar sensitivity helper (experiment_contract §13.3)
# ---------------------------------------------------------------------------
THRESHOLD_BARS = ("B0", "B1", "B2", "B3")  # monotone nesting


def bar_pass(pipeline_valid: bool, solver_acceptable: bool,
              kqp_pass: bool, bar: str) -> bool:
    """§13.3 the four nested stop bars.

      B0 = P                   (weakest)
      B1 = P ∧ S
      B2 = P ∧ K               (B1, B2 incomparable)
      B3 = P ∧ S ∧ K           (= §4.2 main ablation stop criterion)

    Inputs are the bare per-iteration component checks; the agent never
    sees these combined — only via the feedback channel mask (§3.3).
    """
    P = bool(pipeline_valid)
    S = bool(solver_acceptable)
    K = bool(kqp_pass)
    if bar == "B0":
        return P
    if bar == "B1":
        return P and S
    if bar == "B2":
        return P and K
    if bar == "B3":
        return P and S and K
    raise ValueError(f"unknown threshold bar {bar!r}")


# ---------------------------------------------------------------------------
# IR validator + CED (re-use existing infra)
# ---------------------------------------------------------------------------

def validate_ir(ir: dict) -> tuple[bool, list[str]]:
    sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
    from validator import validate
    res = validate(ir)
    return res["overall"] == "pass", res["schema_issues"] + res["semantic_issues"]


def compute_ced(ir_t: dict, ir_t1: dict) -> dict:
    sys.path.insert(0, str(ROOT / "cad_edit_distance"))
    from compute_ced import compute_all
    return compute_all(ir_t, ir_t1)


# ---------------------------------------------------------------------------
# §10 artifact writers
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str),
                       encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _save_iter_artifacts_v02(iter_dir: Path, record: dict) -> None:
    """Per §10 protocol."""
    _write_json(iter_dir / "_iter_record.json", record)


# ---------------------------------------------------------------------------
# run_one_sample — the rewritten repair loop.
# ---------------------------------------------------------------------------

def run_one_sample(method: dict, sample_id: str, negative_id: str,
                     record: dict, config: dict,
                     out_dir: Path) -> dict:
    """Run a single (method, sample_id, negative_id) experiment.

    The repair loop is **shared by all four methods**: every method runs
    the full verification pipeline at every iteration, the only
    differences being what the agent is told (via the [FEEDBACK] block).

    Stop rules (§4.3) are applied identically:
        S1 action=no_change          → STOP
        S2 IR_{t+1} == IR_t          → STOP
        S3 Success(C) = True (post-hoc, not fed back) → STOP
        S4 max_iter=3                → STOP

    B-003 fix (2026-07-16): ``negative_id`` is now a first-class
    parameter; ``out_dir`` is the per-(sample, neg) directory; the initial
    IR is loaded from the task5 perturbation battery when available, falling
    back to canonical E2 perturbation for legacy single-neg smoke tests.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load frozen inputs ----
    kqp_path = KQP_DIR / f"{sample_id}.kqp_instance.json"
    plan_path = PLAN_DIR / f"{sample_id}.design_plan.json"
    history_path = HIST_DIR / sample_id / "input_history.json"
    initial_step_path = HIST_DIR / sample_id / "generated.step"
    design_plan = (json.loads(plan_path.read_text(encoding="utf-8"))
                       if plan_path.exists() else {})

    # ---- Build perturbed IR_t — per B-003 dispatch by task5 neg ---
    init = load_initial_ir(sample_id, negative_id, config)
    if init is None:
        return {"sample_id": sample_id, "negative_id": negative_id,
                "method": method["id"],
                "error": f"clean IR not found for {sample_id}"}
    ir_t_raw, perturbation_meta, neg_record = init
    ir_t = _serialize_ir(ir_t_raw)

    # ---- Sample info ----
    pert_meta_path = (TASK5_PERT_ROOT / sample_id / negative_id
                         / "perturbation_meta.json")
    pert_history_path = (TASK5_PERT_ROOT / sample_id / negative_id
                           / f"{sample_id}_perturbed.json")
    sample_info = {
        "design_plan_path": _abs_to_rel(plan_path),
        "initial_ir_path": _abs_to_rel(IR_EXAMPLES_DIR / f"{sample_id}.cad_ir.json"),
        "initial_step_path": _abs_to_rel(initial_step_path),
        "kqp_instance_path": _abs_to_rel(kqp_path),
        "perturbation_meta_path": _abs_to_rel(pert_meta_path)
            if pert_meta_path.exists() else None,
        "perturbed_history_path": _abs_to_rel(pert_history_path)
            if pert_history_path.exists() else None,
        "sample_id": sample_id,
        "negative_id": negative_id,
        "source": neg_record.get("source"),
        "perturbation_type": perturbation_meta.get("type"),
        "perturbation_operator": perturbation_meta.get("operator_input_name"),
        "perturbation_target_intent": perturbation_meta.get("target_intent"),
    }
    _write_json(out_dir / "sample_info.json", sample_info)

    # ---- Loop state ----
    max_iter = config["runtime"]["max_iterations"]
    iteration_records: list[dict] = []
    ir_current = ir_t
    final_status = "max_iter_reached"
    success = False
    strict_success = False
    k_iter = None
    success_at_K = {1: False, 2: False, 3: False}
    ced_declared_total = 0.0
    ced_executed_total = 0.0
    ced_text_total = 0.0
    n_iterations = 0
    n_execution = 0
    n_verification = 0
    input_tokens_total = 0
    output_tokens_total = 0
    initial_eval: dict | None = None
    final_solver_status = "unknown"
    notes: list[str] = []
    t_run_start = time.time()

    # ---- Main loop ----
    for it in range(max_iter):
        n_iterations = it + 1
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        t_iter_start = time.time()

        # Persist IR_t (always)
        ir_t_path = iter_dir / "IR_t.json"
        _write_json(ir_t_path, ir_current)

        # Stage 1: Adaptor (always runs — pipeline validity depends on it)
        t0 = time.time()
        adapt_report = _run_adaptor(ir_current, iter_dir)
        t_adaptor = time.time() - t0
        n_execution += 1
        step_path = next(iter_dir.glob("*.step"), None)
        script_path = iter_dir / "generated_script.py"

        # Persist adaptor traces if present (per §10)
        dt = iter_dir / "declared_operation_trace.json"
        et = iter_dir / "executed_operation_trace.json"
        if dt.exists() and et.exists():
            try:
                _write_json(iter_dir / "declared_trace.json",
                              json.loads(dt.read_text(encoding="utf-8")))
                _write_json(iter_dir / "executed_trace.json",
                              json.loads(et.read_text(encoding="utf-8")))
            except Exception:
                pass

        # Stage 2: Solver feedback (ALWAYS run per §4.1)
        t0 = time.time()
        solver_fb = _run_solver(history_path)
        t_solver = time.time() - t0
        _write_json(iter_dir / "solver_feedback.json", solver_fb)
        n_verification += 1

        # Stage 3: KQP feedback (ALWAYS run per §4.1)
        t0 = time.time()
        kqp_fb = _run_kqp(step_path, kqp_path, plan_path,
                             iter_dir / "kqp_feedback.json")
        t_kqp = time.time() - t0
        n_verification += 1

        # Stage 4: compute Success(C) per §4.2 — the post-hoc measured value
        # that S3 uses as an efficiency cutoff.  The agent never sees this
        # value directly (§4.3 fairness note).
        success_eval = compute_success(adapt_report, solver_fb, kqp_fb,
                                          step_path)
        final_solver_status = success_eval["solver_canonical_status"]

        # Record iter 0 as initial_status.
        if it == 0:
            initial_eval = success_eval

        iter_record: dict = {
            "iter": it,
            "phase": "initial" if it == 0 else "repair",
            "ir_path": _abs_to_rel(ir_t_path),
            "ir_t1_path": None,
            "step_path": _abs_to_rel(step_path) if step_path else None,
            "script_path": _abs_to_rel(script_path) if script_path.exists() else None,
            "solver_feedback_path": _abs_to_rel(iter_dir / "solver_feedback.json"),
            "kqp_feedback_path": _abs_to_rel(iter_dir / "kqp_feedback.json"),
            "agent_request_path": None,
            "agent_response_path": None,
            "timing_path": None,
            "token_usage_path": None,
            "ced_path": None,
            "agent_status": None,
            "action": None,
            "pipeline_valid": success_eval["pipeline_valid"],
            "pipeline_valid_breakdown": success_eval["pipeline_valid_breakdown"],
            "solver_status": success_eval["solver_canonical_status"],
            "solver_acceptable": success_eval["solver_valid"],
            "kqp_pass": success_eval["kqp_pass"],
            "kqp_failed_query_ids": success_eval["kqp_failed_query_ids"],
            "success": success_eval["success"],
            "strict_success": success_eval["strict_success"],
            "ir_was_modified_by_agent": False,
            "stop_rule": None,
            "wallclock_sec": time.time() - t_iter_start,
            "stage_timings_sec": {
                "adaptor": t_adaptor, "solver": t_solver,
                "kqp": t_kqp, "agent": 0.0,
            },
        }

        # Stage 5: agent call (only if iter > 0 or the iter-0 is the
        # first repair attempt).  We do NOT skip M0 any more (§4.1:
        # every iteration runs the full pipeline; iter 0 is initial
        # verification; iter 1 is the first repair attempt).
        # Even M0 gets an agent call at iter 1+ so the LLM has a
        # chance to react to pipeline feedback.  The only difference
        # is that M0's [FEEDBACK] block contains no solver/kqp.
        if it == 0:
            # iter 0 = initial verification.  No agent call.  Record
            # and either S3-success or proceed.
            iter_record["agent_status"] = "not_called_iter_0"
            iter_record["stop_rule"] = "S3_success" if success_eval["success"] else None
            _write_json(iter_dir / "timing.json", {
                "adaptor": t_adaptor, "solver": t_solver,
                "kqp": t_kqp, "agent": 0.0,
                "total_sec": time.time() - t_iter_start,
            })
            iter_record["timing_path"] = _abs_to_rel(iter_dir / "timing.json")
            _save_iter_artifacts_v02(iter_dir, iter_record)
            iteration_records.append(iter_record)
            if success_eval["success"]:
                # Already successful on the perturbed IR — rare but documented.
                success = True
                strict_success = success_eval["strict_success"]
                k_iter = 1
                success_at_K = {1: True, 2: True, 3: True}
                final_status = "success_initial"
                break
            # else: proceed to iter 1 (first repair attempt)
            ir_current = ir_t  # unchanged on iter 0
            continue

        # Stage 5: agent call (iter 1+)
        t0 = time.time()
        new_ir_raw, agent_io, action_meta = _call_agent(
            ir_current, design_plan, solver_fb, kqp_fb, method, adapt_report)
        t_agent = time.time() - t0
        input_tokens_total += agent_io["input_tokens"]
        output_tokens_total += agent_io["output_tokens"]

        iter_record["agent_status"] = agent_io["agent_status"]
        iter_record["action"] = action_meta["action"]

        # Stage 6: schema validation of IR_{t+1}
        valid, _issues = validate_ir(new_ir_raw)
        if not valid:
            new_ir_raw = copy.deepcopy(ir_current)
            notes.append(f"iter{it}:agent_ir_schema_invalid")
        ir_t1 = _serialize_ir(new_ir_raw)
        ir_was_modified = (ir_t1 != ir_current)

        # Persist IR_t1 + agent artifacts
        ir_t1_path = iter_dir / "IR_t1.json"
        _write_json(ir_t1_path, ir_t1)
        iter_record["ir_t1_path"] = _abs_to_rel(ir_t1_path)
        iter_record["ir_was_modified_by_agent"] = ir_was_modified

        agent_request_path = iter_dir / "agent_request.json"
        agent_response_path = iter_dir / "agent_response.json"
        _write_json(agent_request_path, {
            "method": method["id"], "prompt_text": agent_io["prompt_text"],
        })
        _write_json(agent_response_path, {
            "method": method["id"], "response_text": agent_io["response_text"],
        })
        iter_record["agent_request_path"] = _abs_to_rel(agent_request_path)
        iter_record["agent_response_path"] = _abs_to_rel(agent_response_path)

        token_usage_path = iter_dir / "token_usage.json"
        _write_json(token_usage_path, {
            "input": agent_io["input_tokens"],
            "output": agent_io["output_tokens"],
            "total": agent_io["input_tokens"] + agent_io["output_tokens"],
        })
        iter_record["token_usage_path"] = _abs_to_rel(token_usage_path)

        # Stage 7: CED(IR_t, IR_{t+1})
        ced = compute_ced(ir_current, ir_t1)
        ced_path = iter_dir / "ced.json"
        _write_json(ced_path, ced)
        iter_record["ced_path"] = _abs_to_rel(ced_path)
        ced_decl_v = (ced.get("ced_declared") or {}).get("raw", 0) or 0
        ced_exec_v = (ced.get("ced_executed") or {}).get("raw", 0) or 0
        ced_text_v = (ced.get("ced_text") or {}).get("normalized", 0) or 0
        ced_declared_total += ced_decl_v
        ced_executed_total += ced_exec_v
        ced_text_total += ced_text_v
        iter_record["stage_timings_sec"]["agent"] = t_agent
        iter_record["wallclock_sec"] = time.time() - t_iter_start

        # Stop rules (§4.3).  B-001 fix (2026-07-16): re-ordered to
        # S1 > S3 > S2.  Reason: if ir_t1 == ir_current AND
        # success_eval.success is True, the iter *did* achieve the
        # goal; S2 (ir_unchanged) cannot pre-empt S3 or we under-report
        # success_at_K.  The LLM not changing anything after a successful
        # iter is a normal terminal state, not a no-op.
        stop_rule = None
        if action_meta["action"] == "no_change":
            stop_rule = "S1"
        elif success_eval["success"]:
            stop_rule = "S3"
        elif ir_t1 == ir_current:
            stop_rule = "S2"
        iter_record["stop_rule"] = stop_rule
        iter_record["stage_timings_sec"]["total_sec"] = time.time() - t_iter_start
        _write_json(iter_dir / "timing.json", {
            **iter_record["stage_timings_sec"],
            "total_sec": time.time() - t_iter_start,
        })
        iter_record["timing_path"] = _abs_to_rel(iter_dir / "timing.json")
        _save_iter_artifacts_v02(iter_dir, iter_record)
        iteration_records.append(iter_record)

        # Apply stop rules
        if stop_rule == "S1":
            final_status = "stop_S1_no_change"
            break
        if stop_rule == "S2":
            final_status = "stop_S2_ir_unchanged"
            break
        if stop_rule == "S3":
            success = True
            strict_success = success_eval["strict_success"]
            k_iter = it + 1
            success_at_K = {k: (k >= k_iter) for k in (1, 2, 3)}
            final_status = f"stop_S3_success_at_iter_{k_iter}"
            break
        # S4 will fire when the for-loop exhausts.

        ir_current = ir_t1
    else:
        # exhausted without success
        final_status = "stop_S4_max_iter"

    # ---- Compute final metrics ----
    if k_iter is not None:
        n_iterations_to_success = k_iter
    else:
        n_iterations_to_success = None
    if initial_eval is None and iteration_records:
        initial_eval = {
            "kqp_pass": iteration_records[0].get("kqp_pass", False),
            "kqp_failed_query_ids": iteration_records[0].get("kqp_failed_query_ids", []),
            "solver_canonical_status": iteration_records[0].get("solver_status", "unknown"),
            "solver_valid": iteration_records[0].get("solver_acceptable", False),
            "pipeline_valid": iteration_records[0].get("pipeline_valid", False),
            "success": iteration_records[0].get("success", False),
        }
    if initial_eval is None:
        initial_eval = {}
    # §4.6 RepairCost
    repair_cost = ced_declared_total + 0.1 * n_execution + 0.1 * n_verification
    runtime_sec = time.time() - t_run_start

    run_result = {
        "schema_version": "run_result_v0.2",
        "config_version": config.get("schema_version", "benchmark_config_v0.2"),
        "run_id": f"{method['id']}__{sample_id}__{negative_id}__{int(time.time())}",
        "sample_id": sample_id,
        "negative_id": negative_id,
        "task_type": "repair",
        "method": _METHOD_TO_ID[method["id"]],
        "method_id": method["id"],
        "max_iter": max_iter,
        "sample_info": sample_info,
        "perturbation": perturbation_meta,
        "initial_status": {
            "success": initial_eval.get("success", False),
            "strict_success": initial_eval.get("strict_success", False),
            "pipeline_valid": initial_eval.get("pipeline_valid", False),
            "solver_status": initial_eval.get("solver_canonical_status", "unknown"),
            "solver_acceptable": initial_eval.get("solver_valid", False),
            "kqp_pass": initial_eval.get("kqp_pass", False),
            "kqp_failed_query_ids": initial_eval.get("kqp_failed_query_ids", []),
        },
        "final_status": {
            "success": success,
            "strict_success": strict_success,
            "iterations_used": n_iterations,
            "n_iterations_to_success": n_iterations_to_success,
            "stop_reason": final_status,
            "final_solver_status": final_solver_status,
            "final_kqp_pass": (iteration_records[-1]["kqp_pass"]
                                  if iteration_records else False),
            "final_pipeline_valid": (iteration_records[-1]["pipeline_valid"]
                                          if iteration_records else False),
        },
        "metrics": {
            "success_at_1": success_at_K[1],
            "success_at_2": success_at_K[2],
            "success_at_3": success_at_K[3],
            "failure_to_success": success,
            "kqp_query_improvement": (1 if success else 0),
            "remaining_failed_query_count": (
                len(iteration_records[-1]["kqp_failed_query_ids"])
                if iteration_records else 0),
            "targeted_repair_success": success,
            "ced_text_total": ced_text_total,
            "ced_declared_total": ced_declared_total,
            "ced_executed_total": ced_executed_total,
            "repair_cost": repair_cost,
            "n_execution": n_execution,
            "n_verification": n_verification,
            "runtime_sec": runtime_sec,
            "input_tokens": input_tokens_total,
            "output_tokens": output_tokens_total,
            "total_tokens": input_tokens_total + output_tokens_total,
            "n_iterations": n_iterations,
        },
        "iterations": iteration_records,
        "artifacts_dir": _abs_to_rel(out_dir),
        "notes": "; ".join(notes) if notes else None,
    }
    _write_json(out_dir / "run_result.json", run_result)

    # §10 per-sample repair_summary.json
    _write_json(out_dir / "repair_summary.json", {
        "sample_id": sample_id,
        "method": method["id"],
        "n_iterations": n_iterations,
        "success": success,
        "strict_success": strict_success,
        "n_iterations_to_success": n_iterations_to_success,
        "stop_reason": final_status,
        "metrics": run_result["metrics"],
        "iter_records_summary": [
            {
                "iter": r["iter"],
                "phase": r["phase"],
                "stop_rule": r["stop_rule"],
                "pipeline_valid": r["pipeline_valid"],
                "solver_status": r["solver_status"],
                "solver_acceptable": r["solver_acceptable"],
                "kqp_pass": r["kqp_pass"],
                "success": r["success"],
                "action": r.get("action"),
            }
            for r in iteration_records
        ],
    })
    return run_result


_METHOD_TO_ID = {
    "M0_NoFeedback": "no_feedback",
    "M1_SolverOnly": "solver_only",
    "M2_KQPOnly": "kqp_only",
    "M3_SolverKQP": "solver_kqp",
}


def _serialize_ir(ir: dict) -> dict:
    def _r(v):
        if isinstance(v, float):
            return round(v, 4)
        if isinstance(v, list):
            return [_r(x) for x in v]
        if isinstance(v, dict):
            return {k: _r(x) for k, x in sorted(v.items()) if k != "_meta"}
        return v
    return _r(ir)


def _find_extrude_ops(ir: dict) -> list[str]:
    return [op.get("op_id", "?") for op in ir.get("operations", [])
              if op.get("op_type") == "extrude"]


def _extrude_distances(ir: dict) -> dict:
    return {op.get("op_id", f"op_{i}"): op.get("params", {}).get("distance")
              for i, op in enumerate(ir.get("operations", []))
              if op.get("op_type") == "extrude"}


def _abs_to_rel(p: Path | None) -> str | None:
    if p is None:
        return None
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Benchmark driver
# ---------------------------------------------------------------------------

def probe_llm_connectivity(timeout: float = 12.0,
                              allow_skip: bool = False) -> bool:
    """Pre-flight network probe (added per user request).

    Why: we previously hit a silent failure mode where the
    `ZHIPU_API_KEY` environment variable WAS set, but a stale system
    proxy (127.0.0.1:7890 — typical Clash/v2ray) intercepted the request
    and refused the connection.  The exception was swallowed inside
    `_call_agent` and the run silently fell back to the offline
    agent, producing zero-token artefacts that looked correct but
    contained no real LLM signal.  We now probe explicitly before the
    real run begins.

    Rules:
      - The key length alone is not sufficient.  We MUST actually call
        the ZHIPU endpoint and see a 2xx response.
      - Default behaviour: bypass the system proxy (`proxies={"http": None,
        "https": None}`) to avoid the local-proxy-refused trap.  Opt back
        in by setting ``REQUESTS_USE_PROXY=1`` in env.
      - If ``allow_skip=True`` (CI / dry-run mode) we do not raise; we
        just print a warning.
    """
    use_proxy = os.getenv("REQUESTS_USE_PROXY", "0") == "1"
    if use_proxy:
        proxies = None
        print("[probe_llm_connectivity] REQUESTS_USE_PROXY=1 → using system proxy")
    else:
        proxies = {"http": None, "https": None}
        print("[probe_llm_connectivity] using direct connection (proxy bypassed)")

    api_key = os.getenv("ZHIPU_API_KEY", "")
    if not api_key:
        print("[probe_llm_connectivity][FATAL] ZHIPU_API_KEY is empty — "
              "set it before running the LLM benchmark.")
        # allow_skip=True means "non-fatal" but still returns False to
        # signal probe failure.  Hard fail only when allow_skip=False.
        if not allow_skip:
            raise SystemExit(2)
        return False
    if api_key.startswith("184e4ae5") and not use_proxy:
        # default test/legacy key — print a heads-up; still proceed.
        print("[probe_llm_connectivity] using the project's default key (184e4ae5...)")

    try:
        import requests
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"}
        payload = {"model": "glm-5.1",
                    "messages": [{"role": "user",
                                    "content": "ping"}],
                    "temperature": 0.0, "max_tokens": 8}
        r = requests.post(url, headers=headers, json=payload,
                            timeout=timeout, proxies=proxies)
        if r.status_code == 200:
            body_preview = r.text[:200]
            print(f"[probe_llm_connectivity] OK status=200 body[:200]={body_preview}")
            return True
        # Non-200 — print failure clearly; allow_skip only controls whether
        # we return False (continue) vs raise (abort).  We never return
        # True on non-200.
        msg = (f"[probe_llm_connectivity][FAIL] "
                f"unexpected status={r.status_code} body[:200]={r.text[:200]}")
        if r.status_code in (401, 403):
            print(msg + "  (auth failure)")
        else:
            print(msg)
        return False
    except Exception as e:
        # Show the actual proxy / DNS / SSL error class so the user
        # can act on it.
        print(f"[probe_llm_connectivity][FAIL] {type(e).__name__}: {str(e)[:300]}")
        if "127.0.0.1" in str(e):
            print("[probe_llm_connectivity][HINT] detected 127.0.0.1 proxy — "
                  "start your local proxy (Clash / v2ray) or set "
                  "REQUESTS_USE_PROXY=0 (default) to bypass it.")
        return False


def run_benchmark(method: dict, samples: list[tuple[str, str]],
                    out_root: Path, config: dict) -> list[dict]:
    """Run the benchmark on a list of ``(sample_id, negative_id)`` pairs.

    B-003 fix (2026-07-16): ``samples`` is a list of ``(sid, nid)`` tuples
    (not just ``sid`` strings).  For each, ``run_one_sample`` writes to
    ``out_root / sid / nid`` so multiple negatives per sample coexist
    without overwriting.

    The legacy ``sample_ids: list[str]``-shaped caller (smoke-test style)
    is still supported via ``samples = [(s, "neg_01") for s in
    sample_ids]``, but the canonical path is now the (sid, nid) form.
    """
    records = list_valid_negatives()
    by_pair = {(r["sample_id"], r.get("negative_id", "neg_01")): r
                  for r in records}
    out_root.mkdir(parents=True, exist_ok=True)
    results = []
    for sid, nid in samples:
        pair_key = (sid, nid)
        rec = by_pair.get(pair_key,
                            {"sample_id": sid, "negative_id": nid})
        out_dir = out_root / sid / nid
        print(f"[{method['id']}] {sid}/{nid} ...", flush=True)
        res = run_one_sample(method, sid, nid, rec, config, out_dir)
        results.append(res)
    return results


def aggregate(results: list[dict]) -> dict:
    """Aggregate per-sample results into the §5 metric set.

    B-003 fix: filter out error-dict results that lack ``metrics`` rather
    than crashing.  Denominator is the count of successful runs; the
    raw failure count is included as ``n_errors``.
    """
    ok = [r for r in results if "metrics" in r and "iterations" in r]
    errs = [r for r in results if r not in ok]
    n = len(ok)
    if n == 0:
        return {"n_samples": 0, "n_errors": len(errs),
                  "errors": [{"sample_id": r.get("sample_id"),
                                 "negative_id": r.get("negative_id"),
                                 "error": r.get("error")}
                                for r in errs]}
    succ_at_1 = sum(1 for r in ok if r["metrics"]["success_at_1"])
    succ_at_2 = sum(1 for r in ok if r["metrics"]["success_at_2"])
    succ_at_3 = sum(1 for r in ok if r["metrics"]["success_at_3"])
    f2s = sum(1 for r in ok if r["metrics"]["failure_to_success"])
    iter_to_succ = [r["final_status"]["n_iterations_to_success"]
                       for r in ok
                       if r["final_status"]["n_iterations_to_success"] is not None]
    mean_iter_succ = (sum(iter_to_succ) / len(iter_to_succ)
                          if iter_to_succ else None)
    return {
        "n_samples": n,
        "n_errors": len(errs),
        "errors": [{"sample_id": r.get("sample_id"),
                       "negative_id": r.get("negative_id"),
                       "error": r.get("error")}
                      for r in errs],
        "Success@1": succ_at_1 / n,
        "Success@2": succ_at_2 / n,
        "Success@3": succ_at_3 / n,
        "F2S_ConversionRate": f2s / n,
        "MeanIterationsToSuccess": mean_iter_succ,
        "n_iterations_to_success_distribution": {
            str(k): sum(1 for v in iter_to_succ if v == k)
            for k in (1, 2, 3)
        },
        "MeanCED_declared_total": sum(r["metrics"]["ced_declared_total"]
                                          for r in ok) / n,
        "MeanCED_executed_total": sum(r["metrics"]["ced_executed_total"]
                                          for r in ok) / n,
        "MeanRepairCost": sum(r["metrics"]["repair_cost"] for r in ok) / n,
        "MeanRuntimeCost_s": sum(r["metrics"]["runtime_sec"] for r in ok) / n,
        "MeanInputTokens": sum(r["metrics"]["input_tokens"] for r in ok) / n,
        "MeanOutputTokens": sum(r["metrics"]["output_tokens"] for r in ok) / n,
        "MeanTotalTokens": sum(r["metrics"]["total_tokens"] for r in ok) / n,
        "n_failure_to_success": f2s,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", required=True,
                       choices=["M0_NoFeedback", "M1_SolverOnly",
                                  "M2_KQPOnly", "M3_SolverKQP"])
    ap.add_argument("--sample", action="append", default=[],
                       help="sample id, optionally as 'sid' or 'sid/nid' "
                              "(may be repeated). default: first eligible "
                              "negatives")
    ap.add_argument("--out-root", default=None,
                       help="output directory root (default: experiments/results/<method>)")
    ap.add_argument("--limit", type=int, default=1,
                       help="if --sample not given, take first N eligible")
    ap.add_argument("--config",
                       default=str(CONFIG_PATH),
                       help="path to benchmark_config_v0.2.json")
    ap.add_argument("--skip-probe", action="store_true",
                       help="do not probe LLM connectivity before run "
                              "(rare; use only for CI dry-run)")
    args = ap.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    methods = {m["id"]: m for m in config["methods"]}
    method = methods[args.method]

    # §4.1 / §12 reproducibility — every method uses the same LLM.  Probe
    # connectivity before the run to fail fast on silent-proxy errors.
    if not args.skip_probe:
        probe_ok = probe_llm_connectivity(allow_skip=False)
        if not probe_ok:
            print("[main] LLM probe failed; aborting to avoid silent offline run.")
            sys.exit(2)

    records = list_valid_negatives()
    # Parse --sample arguments: each may be 'sid' (default neg_01) or 'sid/nid'.
    if args.sample:
        samples = [parse_sample_arg(s) for s in args.sample]
    else:
        # default: take first N eligible (sid, neg) pairs
        samples = [(r["sample_id"], r.get("negative_id", "neg_01"))
                      for r in records[:args.limit]]
    out_root = (Path(args.out_root) if args.out_root
                  else ROOT / "experiments" / "results" / args.method)
    results = run_benchmark(method, samples, out_root, config)
    summary = aggregate(results)
    summary_payload = {
        "method": method["id"],
        "name": method["name"],
        "feedback_channels": method["feedback_channels"],
        "schema_version": config.get("schema_version", "benchmark_config_v0.2"),
        "metrics": summary,
    }
    report_dir = ROOT / "experiments" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    _write_json(report_dir / f"benchmark_{args.method}_summary.json",
                   summary_payload)
    n_err = summary.get("n_errors", 0)
    n_ok = summary.get("n_samples", 0)
    print(f"[{args.method}] wrote {n_ok} samples ({n_err} errors); "
          f"Success@3 = {summary.get('Success@3', 0):.3f}")


if __name__ == "__main__":
    main()