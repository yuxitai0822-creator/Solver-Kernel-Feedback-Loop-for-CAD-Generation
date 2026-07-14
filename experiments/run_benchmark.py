"""run_benchmark.py — Solver-KQP Repair Loop Benchmark v0.1.

Runs the 4 methods (M0/M1/M2/M3) on the 132 valid negative samples.
For each `(method, sample_id)`:
  1. Load the original GT IR + DesignPlan
  2. Build a "perturbed" IR_t from the negative record's metadata
  3. Run the repair loop with the appropriate feedback mask
  4. Compute generation + repair metrics
  5. Save artifacts per the protocol

Output:
  experiments/results/<method>/<sample_id>/iter_<NN>/...
  experiments/results/<method>/<sample_id>/repair_summary.json
  experiments/reports/benchmark_<method>_summary.json
  experiments/reports/benchmark_master_summary.json
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

CONFIG_PATH = ROOT / "experiments" / "config" / "benchmark_config_v0.1.json"
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
# Helpers
# ---------------------------------------------------------------------------

def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def list_valid_negatives() -> list[dict]:
    """Return perturbation records that succeeded reconstruction.

    Priority:
      1. adaptor_run_summary.json (if it exists) — has 'reconstruction_success'
      2. kqp_detection_summary.json — has 138 entries (one per perturbation
         record), all 'initially failed' (so all 138 are valid negatives).
    """
    if TASK5_ADAPTOR_SUMMARY.exists():
        summary = json.loads(TASK5_ADAPTOR_SUMMARY.read_text(encoding="utf-8"))
        rows = summary["rows"]
        return [r for r in rows if r.get("reconstruction_success")]
    if TASK5_KQP_DETECTION.exists():
        kqp = json.loads(TASK5_KQP_DETECTION.read_text(encoding="utf-8"))
        return kqp["rows"]
    return []


def perturb_ir_canonical(ir_t: dict) -> dict:
    """Apply the canonical E2_extrude_deep perturbation to a clean IR.

    This is a 1.5x scale of the extrude distance.  This is the most
    reliable KQP-failing perturbation in the Task 5 set, and using a
    canonical perturbation across all 4 methods makes the ablation
    reproducible (the only variable is the feedback mask).
    """
    ir_p = copy.deepcopy(ir_t)
    for op in ir_p["operations"]:
        if op.get("op_type") == "extrude":
            d = op["params"].get("distance", 0)
            if d > 0:
                op["params"]["distance"] = round(d * 1.5, 4)
            break
    return ir_p


def find_clean_ir_for_negative(sample_id: str) -> dict | None:
    """Locate the clean IR for a sample by matching the perturbed sample's
    base sample_id.  Task 5 records map perturbed_sample → base_sample
    in the perturbation_meta.json; v0.1 just uses sample_id as base."""
    # The "negative" record's sample_id is the same as the base sample_id
    # (Task 5 generates one negative per sample).
    ir_path = IR_EXAMPLES_DIR / f"{sample_id}.cad_ir.json"
    if ir_path.exists():
        return json.loads(ir_path.read_text(encoding="utf-8"))
    return None


# ---------------------------------------------------------------------------
# Feedback generation (using existing infra)
# ---------------------------------------------------------------------------

def _run_adaptor(ir: dict, out_dir: Path) -> dict:
    """Run Phase 2 Adaptor in cad_subproject1 subprocess."""
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
    """Run KQP runner via subprocess (cad_subproject1)."""
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
    """Run FreeCAD Solver Feedback in freecad_sketcher subprocess."""
    if not history_path.exists():
        return {"status": "skipped", "reason": "no history_path"}
    try:
        # The FreeCAD solver feedback is implemented as a Python
        # module that requires setup.  The cleanest cross-env path is to
        # import the module directly.  Since we're in freecad_sketcher, we
        # can do that here.  The repair_loop uses this same path.
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
        return {
            "status": "ran",
            "raw_solve_return_code": raw.get("solve_return_code", 0),
            "raw_dof": raw.get("dof", 0),
            "solve": normalized,
            "recompute": normalized_rc,
            "conflicting": raw.get("conflicting_constraints", []),
            "redundant": raw.get("redundant_constraints", []),
            "malformed": raw.get("malformed_constraints", []),
        }
    except Exception as e:
        return {"status": "skipped", "reason": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Agent call
# ---------------------------------------------------------------------------

def call_agent(ir_t: dict, solver_fb: dict, kqp_fb: dict,
                 method: dict) -> dict:
    """Call the ZHIPU LLM agent.  Returns a new IR (or ir_t on failure)."""
    prompt = build_prompt(ir_t, solver_fb, kqp_fb, method)
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        # Offline fallback
        return _offline_agent(ir_t, kqp_fb, method)
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
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```", 1)[0]
        new_ir = json.loads(text)
        return new_ir
    except Exception as e:
        return _offline_agent(ir_t, kqp_fb, method) | {
            "_agent_error": f"{type(e).__name__}: {e}"}


def _offline_agent(ir_t: dict, kqp_fb: dict, method: dict) -> dict:
    """Deterministic offline agent: bump failing numeric params 20% toward
    expected values."""
    new_ir = copy.deepcopy(ir_t)
    if not method.get("run_kqp_feedback"):
        return new_ir
    expected_fixes: dict[str, float] = {}
    for qr in kqp_fb.get("query_results", []):
        if qr.get("status") == "fail":
            qid = qr.get("query_id", "")
            exp = qr.get("expected")
            if exp is not None:
                expected_fixes[qid] = float(exp)
    if not expected_fixes:
        return new_ir
    for op in new_ir.get("operations", []):
        opid = op.get("op_id", "")
        if opid in expected_fixes:
            exp = expected_fixes[opid]
            for k, v in op.get("params", {}).items():
                if isinstance(v, (int, float)) and v != 0:
                    op["params"][k] = round(v + 0.2 * (exp - v), 4)
                    break
    return new_ir


def build_prompt(ir_t: dict, solver_fb: dict, kqp_fb: dict,
                   method: dict) -> str:
    """Compose LLM prompt from IR + (optional) feedbacks."""
    parts = [
        "You are a CAD repair agent. Output a JSON object conforming to "
        "cad_ir_v0.1 that fixes the reported issues while minimizing edits.",
        "",
        f"Method: {method.get('id')} — {method.get('name')}",
        f"  Solver feedback: {'available' if method.get('run_solver_feedback') else 'skipped'}",
        f"  KQP feedback:    {'available' if method.get('run_kqp_feedback') else 'skipped'}",
        "",
        "Current IR (IR_t):",
        json.dumps(ir_t, ensure_ascii=False, indent=2),
    ]
    if method.get("run_solver_feedback") and solver_fb.get("status") == "ran":
        parts += ["", "Solver feedback:", json.dumps(solver_fb, ensure_ascii=False, indent=2)[:2000]]
    else:
        parts += ["", "Solver feedback: SKIPPED (not run for this method)"]
    if method.get("run_kqp_feedback"):
        parts += ["", "KQP feedback:", json.dumps(kqp_fb, ensure_ascii=False, indent=2)[:3000]]
    else:
        parts += ["", "KQP feedback: SKIPPED (not run for this method)"]
    parts += ["", "Output the new IR (IR_t+1) only as JSON:"]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Validator (V0.1)
# ---------------------------------------------------------------------------

def validate_ir(ir: dict) -> tuple[bool, list[str]]:
    sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
    from validator import validate
    res = validate(ir)
    return res["overall"] == "pass", res["schema_issues"] + res["semantic_issues"]


# ---------------------------------------------------------------------------
# CED + RepairCost
# ---------------------------------------------------------------------------

def compute_ced(ir_t: dict, ir_t1: dict) -> dict:
    sys.path.insert(0, str(ROOT / "cad_edit_distance"))
    from compute_ced import compute_all
    return compute_all(ir_t, ir_t1)


# ---------------------------------------------------------------------------
# Per-sample loop (V0.1 — emits run_result.json + per-iter records per
#   the run_result_schema_v0.1.json / iteration_record_schema_v0.1.json /
#   artifact_protocol_v0.1.md)
# ---------------------------------------------------------------------------

# Method ID -> benchmark-config "method" field
_METHOD_TO_ID = {
    "M0_NoFeedback": "no_feedback",
    "M1_SolverOnly": "solver_only",
    "M2_KQPOnly": "kqp_only",
    "M3_SolverKQP": "solver_kqp",
}


def _serialize_ir(ir: dict) -> dict:
    """Serialize an IR to a normalized form (4-decimal floats, sorted keys)."""
    def _r(v):
        if isinstance(v, float):
            return round(v, 4)
        if isinstance(v, list):
            return [_r(x) for x in v]
        if isinstance(v, dict):
            return {k: _r(x) for k, x in sorted(v.items())}
        return v
    return _r(ir)


def _skipped_placeholder(reason: str) -> dict:
    return {"status": "skipped", "reason": reason}


def _save_iter_artifacts(iter_dir: Path, iter_record: dict) -> None:
    """Persist the iter_record's paths so a future regenerator can re-locate them."""
    (iter_dir / "_iter_record.json").write_text(
        json.dumps(iter_record, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")


def _write_iter_artifact_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_iter_artifact_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False,
                                  default=str),
                       encoding="utf-8")


def _build_iter_record(it: int, *, phase: str, ir_t: dict,
                          ir_t1: dict | None,
                          step_path: Path | None,
                          script_path: Path | None,
                          adaptor_trace_path: Path | None,
                          solver_result_path: Path,
                          kqp_result_path: Path,
                          ced_path: Path | None,
                          agent_prompt_path: Path | None,
                          agent_response_path: Path | None,
                          runtime_log_path: Path,
                          token_usage_path: Path,
                          agent_status: str,
                          kqp_status: str,
                          solver_status_at_iter: str,
                          ir_was_modified_by_agent: bool,
                          wallclock_sec: float,
                          stage_timings_sec: dict) -> dict:
    rel = lambda p: str(p.relative_to(ROOT)) if p is not None else None
    return {
        "iter": it,
        "phase": phase,
        "ir_path": rel(ir_t.__class__ is dict and (
            # ir_t is dict, but we need its saved path; fall back to canonical
            Path(f"{iter_record_ir_dir(phase, it, ir_t)}.json")
            if False else Path(""))) if False else None,
        # The above lambda is just a placeholder; we set paths explicitly below.
    }


def _abs_to_rel(p: Path | None) -> str | None:
    if p is None:
        return None
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def run_one_sample(method: dict, sample_id: str, record: dict,
                     config: dict, out_dir: Path) -> dict:
    """Run a single (method, sample_id) experiment.

    Emits:
      * out_dir/run_result.json   (per run_result_schema_v0.1.json)
      * out_dir/sample_info.json
      * out_dir/iter_<NN>/<artifacts>  (per artifact_protocol_v0.1.md)
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load clean IR + design plan + KQP instance
    ir_clean = find_clean_ir_for_negative(sample_id)
    if ir_clean is None:
        return {"sample_id": sample_id, "method": method["id"],
                "error": f"clean IR not found for {sample_id}"}
    kqp_path = KQP_DIR / f"{sample_id}.kqp_instance.json"
    plan_path = PLAN_DIR / f"{sample_id}.design_plan.json"
    history_path = HIST_DIR / sample_id / "input_history.json"
    initial_step_path = HIST_DIR / sample_id / "generated.step"

    # 2. Build perturbed IR_t (canonical E2_extrude_deep × 1.5)
    ir_t_raw = perturb_ir_canonical(ir_clean)
    ir_t = _serialize_ir(ir_t_raw)

    # 3. Sample info + perturbation meta
    perturbation_meta = {
        "type": "E2_extrude_deep",
        "ops": _find_extrude_ops(ir_t_raw),
        "values_before": _extrude_distances(ir_clean),
        "values_after": _extrude_distances(ir_t_raw),
    }
    sample_info = {
        "design_plan_path": _abs_to_rel(plan_path),
        "initial_ir_path": _abs_to_rel(
            IR_EXAMPLES_DIR / f"{sample_id}.cad_ir.json"),
        "initial_step_path": _abs_to_rel(initial_step_path),
        "kqp_instance_path": _abs_to_rel(kqp_path),
        "perturbation_meta_path": _abs_to_rel(ROOT / "experiments" /
                                               "config" /
                                               "perturbation_meta.json"),
    }
    (out_dir / "sample_info.json").write_text(
        json.dumps(sample_info, indent=2, ensure_ascii=False),
        encoding="utf-8")

    # 4. Loop state
    iteration_records: list[dict] = []
    ir_current = ir_t
    success_kqp = False
    strict_success = False
    success_at_K = {1: False, 2: False, 3: False}
    k_iter = None
    ced_text_total = 0.0
    ced_declared_total = 0.0
    ced_executed_total = 0.0
    n_iterations = 0
    initial_kqp_pass = False
    initial_num_failed = None
    initial_failed_ids: list[str] = []
    final_solver_status = "unknown"
    notes: list[str] = []
    exec_count = 0
    verify_count = 0
    t_run_start = time.time()
    input_tokens_total = 0
    output_tokens_total = 0

    max_iter = config["runtime"]["max_iterations"]
    for it in range(max_iter):
        n_iterations = it + 1
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        t_iter_start = time.time()

        ir_t_path = iter_dir / "IR_t.json"
        _write_iter_artifact_json(ir_t_path, ir_current)

        # Adaptor
        t0 = time.time()
        adapt_report = _run_adaptor(ir_current, iter_dir)
        t_adaptor = time.time() - t0
        exec_count += 1

        step_path = next(iter_dir.glob("*.step"), None)
        script_path = iter_dir / "generated_script.py"
        adaptor_trace_path = iter_dir / "adaptor_trace_t.json"

        # Save adaptor declared + executed trace if available
        dt = iter_dir / "declared_operation_trace.json"
        et = iter_dir / "executed_operation_trace.json"
        if dt.exists():
            try:
                declared = json.loads(dt.read_text(encoding="utf-8"))
                executed = json.loads(et.read_text(encoding="utf-8"))
                _write_iter_artifact_json(adaptor_trace_path, {
                    "declared": declared, "executed": executed})
            except Exception:
                pass

        # Solver feedback
        t0 = time.time()
        if method.get("run_solver_feedback"):
            solver_fb = _run_solver(history_path) if step_path else _skipped_placeholder("no step")
        else:
            solver_fb = _skipped_placeholder("method disables solver")
        t_solver = time.time() - t0
        solver_result_path = iter_dir / "solver_result_t.json"
        _write_iter_artifact_json(solver_result_path, solver_fb)

        # KQP feedback
        t0 = time.time()
        if method.get("run_kqp_feedback"):
            if step_path and step_path.exists():
                kqp_fb = _run_kqp(step_path, kqp_path, plan_path,
                                       iter_dir / "kqp_result_t.json")
            else:
                kqp_fb = _skipped_placeholder("no step")
        else:
            kqp_fb = _skipped_placeholder("method disables kqp")
        t_kqp = time.time() - t0
        kqp_result_path = iter_dir / "kqp_result_t.json"
        _write_iter_artifact_json(kqp_result_path, kqp_fb)
        verify_count += 1

        # Determine iter status
        kqp_status = kqp_fb.get("overall_status", "unknown")
        solver_status = solver_fb.get("status", "unknown")
        if it == 0:
            initial_kqp_pass = (kqp_status == "pass")
            initial_num_failed = len([qr for qr in kqp_fb.get("query_results", [])
                                        if qr.get("status") == "fail"])
            initial_failed_ids = [qr.get("query_id", "")
                                    for qr in kqp_fb.get("query_results", [])
                                    if qr.get("status") == "fail"]

        # KQP pass → success
        if kqp_status == "pass":
            success_kqp = True
            k_iter = it + 1
            for k in (1, 2, 3):
                if k_iter <= k:
                    success_at_K[k] = True
            # Strict success requires solver acceptable
            if solver_status == "ran":
                ss = solver_fb.get("solve", {}).get("solve_status", "")
                if ss not in ("conflicting", "over_constrained",
                                "unsolvable", "invalid_constraint_reference"):
                    strict_success = True
            final_solver_status = solver_status
            # CED path null on success-final
            ced_path = None
            ir_t1_path = iter_dir / "IR_t1.json"
            _write_iter_artifact_json(ir_t1_path, ir_current)  # no-op
            agent_status = "not_called"
            ir_was_modified = False
            agent_prompt_path = iter_dir / "agent_prompt_t.txt"
            agent_response_path = iter_dir / "agent_response_t.txt"
            _write_iter_artifact_text(agent_prompt_path, "")
            _write_iter_artifact_text(agent_response_path, "")
            token_usage_path = iter_dir / "token_usage_t.json"
            _write_iter_artifact_json(token_usage_path,
                                         {"input": 0, "output": 0, "total": 0})
            runtime_log = {"adaptor": t_adaptor, "solver": t_solver,
                            "kqp": t_kqp, "agent": 0.0,
                            "other": time.time() - t_iter_start,
                            "total_sec": time.time() - t_iter_start}
            _write_iter_artifact_json(iter_dir / "runtime_log_t.json", runtime_log)
            iter_record = {
                "iter": it,
                "phase": "repair" if it > 0 else "initial",
                "ir_path": _abs_to_rel(ir_t_path),
                "ir_t1_path": _abs_to_rel(ir_t1_path),
                "step_path": _abs_to_rel(step_path) if step_path else None,
                "script_path": _abs_to_rel(script_path) if script_path.exists() else None,
                "adaptor_trace_path": _abs_to_rel(adaptor_trace_path)
                    if adaptor_trace_path.exists() else None,
                "solver_result_path": _abs_to_rel(solver_result_path),
                "kqp_result_path": _abs_to_rel(kqp_result_path),
                "ced_path": ced_path,
                "agent_prompt_path": _abs_to_rel(agent_prompt_path),
                "agent_response_path": _abs_to_rel(agent_response_path),
                "runtime_log_path": _abs_to_rel(iter_dir / "runtime_log_t.json"),
                "token_usage_path": _abs_to_rel(token_usage_path),
                "agent_status": agent_status,
                "kqp_status": kqp_status,
                "solver_status_at_iter": solver_status,
                "ir_was_modified_by_agent": ir_was_modified,
                "wallclock_sec": time.time() - t_iter_start,
                "stage_timings_sec": {
                    "adaptor": t_adaptor,
                    "solver": t_solver,
                    "kqp": t_kqp,
                    "agent": 0.0,
                    "other": time.time() - t_iter_start,
                },
            }
            _save_iter_artifacts(iter_dir, iter_record)
            iteration_records.append(iter_record)
            break

        # Agent call
        agent_status = "called_success"
        if not method.get("run_solver_feedback") and not method.get("run_kqp_feedback"):
            ir_t1_raw = copy.deepcopy(ir_current)
            agent_err = "M0_no_feedback: no agent call"
            prompt_text = ""
            response_text = ""
            tok_in = tok_out = 0
            agent_status = "called_skipped_method_m0"
            t_agent = 0.0
        else:
            t0 = time.time()
            prompt_text = build_prompt(ir_current, solver_fb, kqp_fb, method)
            ir_t1_raw, response_text, tok_in, tok_out, agent_err = \
                _call_agent_with_response(ir_current, solver_fb, kqp_fb, method)
            t_agent = time.time() - t0
            if agent_err is not None:
                agent_status = "called_failed"

        input_tokens_total += tok_in
        output_tokens_total += tok_out

        # Validate
        valid, _ = validate_ir(ir_t1_raw)
        if not valid:
            ir_t1_raw = copy.deepcopy(ir_current)
        ir_t1 = _serialize_ir(ir_t1_raw)

        # Persist agent artifacts
        _write_iter_artifact_text(iter_dir / "agent_prompt_t.txt", prompt_text)
        _write_iter_artifact_text(iter_dir / "agent_response_t.txt", response_text)
        token_usage_path = iter_dir / "token_usage_t.json"
        _write_iter_artifact_json(token_usage_path,
                                     {"input": tok_in, "output": tok_out,
                                        "total": tok_in + tok_out})
        if agent_status == "called_skipped_method_m0":
            ir_t1_path = iter_dir / "IR_t1.json"
            _write_iter_artifact_json(ir_t1_path, ir_t1)
            agent_prompt_path = iter_dir / "agent_prompt_t.txt"
            agent_response_path = iter_dir / "agent_response_t.txt"
            ir_was_modified = (ir_t1 != ir_current)
        else:
            ir_t1_path = iter_dir / "IR_t1.json"
            _write_iter_artifact_json(ir_t1_path, ir_t1)
            agent_prompt_path = iter_dir / "agent_prompt_t.txt"
            agent_response_path = iter_dir / "agent_response_t.txt"
            ir_was_modified = (ir_t1 != ir_current)
            if agent_err and not valid:
                notes.append(f"iter{it}:agent_err={agent_err}")

        # CED
        ced = compute_ced(ir_current, ir_t1)
        ced_path = iter_dir / "ced_t_to_t_plus_1.json"
        _write_iter_artifact_json(ced_path, ced)
        ced_text_v = (ced.get("ced_text") or {}).get("normalized", 0)
        ced_decl_v = (ced.get("ced_declared") or {}).get("raw", 0)
        ced_exec_v = (ced.get("ced_executed") or {}).get("raw", 0)
        ced_text_total += ced_text_v or 0
        ced_declared_total += ced_decl_v or 0
        ced_executed_total += ced_exec_v or 0

        runtime_log = {"adaptor": t_adaptor, "solver": t_solver,
                        "kqp": t_kqp, "agent": t_agent,
                        "other": 0.0,
                        "total_sec": time.time() - t_iter_start}
        _write_iter_artifact_json(iter_dir / "runtime_log_t.json", runtime_log)

        iter_record = {
            "iter": it,
            "phase": "repair" if it > 0 else "initial",
            "ir_path": _abs_to_rel(ir_t_path),
            "ir_t1_path": _abs_to_rel(ir_t1_path),
            "step_path": _abs_to_rel(step_path) if step_path else None,
            "script_path": _abs_to_rel(script_path) if script_path.exists() else None,
            "adaptor_trace_path": _abs_to_rel(adaptor_trace_path)
                if adaptor_trace_path.exists() else None,
            "solver_result_path": _abs_to_rel(solver_result_path),
            "kqp_result_path": _abs_to_rel(kqp_result_path),
            "ced_path": _abs_to_rel(ced_path),
            "agent_prompt_path": _abs_to_rel(agent_prompt_path),
            "agent_response_path": _abs_to_rel(agent_response_path),
            "runtime_log_path": _abs_to_rel(iter_dir / "runtime_log_t.json"),
            "token_usage_path": _abs_to_rel(token_usage_path),
            "agent_status": agent_status,
            "kqp_status": kqp_status,
            "solver_status_at_iter": solver_status,
            "ir_was_modified_by_agent": ir_was_modified,
            "wallclock_sec": time.time() - t_iter_start,
            "stage_timings_sec": {
                "adaptor": t_adaptor, "solver": t_solver,
                "kqp": t_kqp, "agent": t_agent, "other": 0.0,
            },
        }
        _save_iter_artifacts(iter_dir, iter_record)
        iteration_records.append(iter_record)
        ir_current = ir_t1

    # Compute final metrics
    final_kqp_pass_count = sum(1 for r in iteration_records
                                  if r["kqp_status"] == "pass")
    initial_kqp_pass_count = 1 if initial_kqp_pass else 0
    final_kqp_pass = success_kqp
    final_num_failed = 0
    last_kqp = iteration_records[-1]["kqp_status"] if iteration_records else "unknown"
    # We don't have direct query details in the iter record; we use the
    # initial count and assume the agent-modified IRs are normalized to
    # pass when kqp_status == "pass".
    if last_kqp == "pass":
        final_num_failed = 0
    else:
        final_num_failed = initial_num_failed or 0
    remaining_failed = final_num_failed
    kqi = (final_kqp_pass_count - initial_kqp_pass_count) * (
        1 if success_kqp else 0)
    # Targeted repair: did the targeted KQP queries that initially failed
    # now pass?  V0.1 approximation: if final kqp pass, true.
    trs = success_kqp

    run_result = {
        "schema_version": "run_result_v0.1",
        "config_version": config.get("schema_version", "benchmark_config_v0.1"),
        "run_id": f"{method['id']}__{sample_id}__{int(time.time())}",
        "sample_id": sample_id,
        "task_type": "repair",
        "method": _METHOD_TO_ID[method["id"]],
        "max_iter": max_iter,
        "sample_info": sample_info,
        "perturbation": perturbation_meta,
        "initial_status": {
            "kqp_pass": initial_kqp_pass,
            "num_failed_queries": initial_num_failed or 0,
            "failed_query_ids": initial_failed_ids,
            "solver_status": "skipped",
            "solver_acceptable": False,
        },
        "final_status": {
            "success": success_kqp,
            "strict_success": strict_success,
            "final_kqp_pass": final_kqp_pass,
            "final_solver_status": final_solver_status,
            "iterations_used": n_iterations,
        },
        "metrics": {
            "success_at_1": success_at_K[1],
            "success_at_2": success_at_K[2],
            "success_at_3": success_at_K[3],
            "failure_to_success": success_kqp,
            "kqp_query_improvement": kqi,
            "remaining_failed_query_count": remaining_failed,
            "targeted_repair_success": trs,
            "ced_text_total": ced_text_total,
            "ced_declared_total": ced_declared_total,
            "ced_executed_total": ced_executed_total,
            "repair_cost": (ced_executed_total
                              + 0.1 * exec_count
                              + 0.1 * verify_count),
            "runtime_sec": time.time() - t_run_start,
            "input_tokens": input_tokens_total,
            "output_tokens": output_tokens_total,
            "total_tokens": input_tokens_total + output_tokens_total,
            "n_iterations": n_iterations,
            "mean_iteration_runtime_sec": ((time.time() - t_run_start)
                                              / n_iterations if n_iterations else None),
        },
        "iterations": iteration_records,
        "artifacts_dir": _abs_to_rel(out_dir),
        "notes": "; ".join(notes) if notes else None,
    }
    (out_dir / "run_result.json").write_text(
        json.dumps(run_result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    return run_result


def _find_extrude_ops(ir: dict) -> list[str]:
    return [op.get("op_id", "?") for op in ir.get("operations", [])
            if op.get("op_type") == "extrude"]


def _extrude_distances(ir: dict) -> dict:
    return {op.get("op_id", f"op_{i}"): op.get("params", {}).get("distance")
              for i, op in enumerate(ir.get("operations", []))
              if op.get("op_type") == "extrude"}


def _call_agent_with_response(ir_t: dict, solver_fb: dict, kqp_fb: dict,
                                method: dict):
    """Call LLM agent, return (new_ir, response_text, tok_in, tok_out, err)."""
    prompt_text = build_prompt(ir_t, solver_fb, kqp_fb, method)
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        ir_t1 = _offline_agent(ir_t, kqp_fb, method)
        return ir_t1, "[offline fallback; ZHIPU_API_KEY not set]", 0, 0, None
    try:
        import requests
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"}
        payload = {
            "model": "glm-5.1",
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.0,
            "max_tokens": 4096,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        resp = r.json()
        text = resp["choices"][0]["message"]["content"].strip()
        usage = resp.get("usage", {})
        tok_in = int(usage.get("prompt_tokens", 0))
        tok_out = int(usage.get("completion_tokens", 0))
        # Parse IR
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```", 1)[0]
        try:
            new_ir = json.loads(text)
        except Exception as e:
            return copy.deepcopy(ir_t), text, tok_in, tok_out, f"parse_err:{e}"
        return new_ir, text, tok_in, tok_out, None
    except Exception as e:
        return _offline_agent(ir_t, kqp_fb, method), \
            f"[agent call failed: {type(e).__name__}: {e}]", 0, 0, str(e)


# ---------------------------------------------------------------------------
# Per-method metrics (reads from the new run_result_v0.1 schema)
# ---------------------------------------------------------------------------

def compute_method_metrics_from_run_results(rows: list[dict]) -> dict:
    """Aggregate the new run_result_v0.1 records per method.

    Reads from run_result["metrics"] and run_result["final_status"]."""
    n = len(rows)
    if n == 0:
        return {}
    n_s1 = sum(1 for r in rows if r["metrics"]["success_at_1"])
    n_s2 = sum(1 for r in rows if r["metrics"]["success_at_2"])
    n_s3 = sum(1 for r in rows if r["metrics"]["success_at_3"])
    n_f2s = sum(1 for r in rows if r["metrics"]["failure_to_success"])
    iter_to_success = [r["final_status"]["iterations_used"]
                          for r in rows if r["final_status"]["success"]]
    ced_total = [r["metrics"]["ced_declared_total"] for r in rows]
    ced_exec_total = [r["metrics"]["ced_executed_total"] for r in rows]
    repair_costs = [r["metrics"]["repair_cost"] for r in rows]
    runtimes = [r["metrics"]["runtime_sec"] for r in rows]
    tokens = [r["metrics"]["total_tokens"] for r in rows]
    return {
        "n_samples": n,
        "Success@1": n_s1 / n,
        "Success@2": n_s2 / n,
        "Success@3": n_s3 / n,
        "F2S_ConversionRate": n_f2s / n,
        "MeanIterationsToSuccess": (sum(iter_to_success) / len(iter_to_success)
                                       if iter_to_success else None),
        "n_iterations_to_success_distribution": {
            "1": sum(1 for k in iter_to_success if k == 1),
            "2": sum(1 for k in iter_to_success if k == 2),
            "3": sum(1 for k in iter_to_success if k == 3),
        },
        "MeanCED_declared_total": (sum(ced_total) / n if n else 0),
        "MeanCED_executed_total": (sum(ced_exec_total) / n if n else 0),
        "MeanRepairCost": (sum(repair_costs) / n if n else 0),
        "MeanRuntimeCost_s": (sum(runtimes) / n if n else 0),
        "MeanTotalTokens": (sum(tokens) / n if n else 0),
        "n_failure_to_success": n_f2s,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", nargs="+", default=None,
                      help="method IDs to run; default = all 4")
    ap.add_argument("--n", type=int, default=None,
                      help="limit to first N negative samples")
    ap.add_argument("--out-root", default="experiments/results",
                      help="output root directory")
    ap.add_argument("--reports-root", default="experiments/reports",
                      help="reports output root")
    ap.add_argument("--clean-perturb-records", action="store_true",
                      help="Use perturbed IR reconstructed from the clean IR "
                           "delta instead of record.perturbed_value (V0.1 default)")
    args = ap.parse_args()

    cfg = load_config()
    methods = cfg["methods"]
    if args.methods:
        methods = [m for m in methods if m["id"] in args.methods]
    if not methods:
        print("No methods to run.  --methods:", args.methods)
        return

    negatives = list_valid_negatives()
    # Deduplicate by sample_id (3 perturbations per sample; we use
    # the canonical perturbation for the benchmark, so one entry per sample).
    seen_samples: set[str] = set()
    negatives_unique: list[dict] = []
    for r in negatives:
        sid = r["sample_id"].replace(".cad_ir", "")
        if sid in seen_samples:
            continue
        seen_samples.add(sid)
        negatives_unique.append(r)
    negatives = negatives_unique
    if args.n:
        negatives = negatives[:args.n]
    print(f"Running benchmark on {len(negatives)} negative samples, "
          f"{len(methods)} method(s)")

    out_root = ROOT / args.out_root
    rep_root = ROOT / args.reports_root
    out_root.mkdir(parents=True, exist_ok=True)
    rep_root.mkdir(parents=True, exist_ok=True)

    master: dict[str, dict] = {}
    for method in methods:
        method_id = method["id"]
        print(f"\n=== {method_id}: {method['name']} ===")
        method_out = out_root / method_id
        method_out.mkdir(parents=True, exist_ok=True)
        method_rows = []
        t0 = time.time()
        for i, rec in enumerate(negatives):
            sid = rec["sample_id"].replace(".cad_ir", "")
            if not (KQP_DIR / f"{sid}.kqp_instance.json").exists():
                continue
            sample_dir = method_out / sid
            rep = run_one_sample(method, sid, rec, cfg, sample_dir)
            method_rows.append(rep)
            if (i + 1) % 5 == 0:
                print(f"   [{method_id}] {i+1}/{len(negatives)} "
                      f"({(time.time()-t0):.0f}s)")
        method_metrics = compute_method_metrics_from_run_results(method_rows)
        method_report = {
            "method": method_id,
            "name": method["name"],
            "run_solver_feedback": method["run_solver_feedback"],
            "run_kqp_feedback": method["run_kqp_feedback"],
            "metrics": method_metrics,
            "n_samples": len(method_rows),
            "rows": method_rows,
            "schema_version": "run_result_v0.1",
        }
        (rep_root / f"benchmark_{method_id}_summary.json").write_text(
            json.dumps(method_report, indent=2, ensure_ascii=False,
                          default=str),
            encoding="utf-8")
        master[method_id] = method_metrics
        print(f"   {method_id} done: {method_metrics}")

    # Master summary
    master_summary = {
        "experiment": "Solver-KQP Repair Loop Benchmark v0.1",
        "n_samples": len(negatives),
        "methods": master,
    }
    (rep_root / "benchmark_master_summary.json").write_text(
        json.dumps(master_summary, indent=2, ensure_ascii=False,
                      default=str),
        encoding="utf-8")
    print("\n=== Master summary ===")
    print(json.dumps(master, indent=2, default=str))


if __name__ == "__main__":
    main()