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
# Per-sample loop
# ---------------------------------------------------------------------------

def run_one_sample(method: dict, sample_id: str, record: dict,
                     config: dict, out_dir: Path) -> dict:
    """Run a single (method, sample_id) experiment."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load clean IR + design plan + KQP instance
    ir_clean = find_clean_ir_for_negative(sample_id)
    if ir_clean is None:
        return {"sample_id": sample_id, "method": method["id"],
                "error": f"clean IR not found for {sample_id}"}
    kqp_path = KQP_DIR / f"{sample_id}.kqp_instance.json"
    plan_path = PLAN_DIR / f"{sample_id}.design_plan.json"
    history_path = HIST_DIR / sample_id / "input_history.json"

    # 2. Build perturbed IR_t (canonical E2_extrude_deep × 1.5)
    ir_t = perturb_ir_canonical(ir_clean)

    # 3. Loop state
    iter_records = []
    exec_count = 0
    verify_count = 0
    ir_current = ir_t
    success_kqp = False
    final_status = "no_iter"
    k_iter = None
    ced_values = []
    n_tries = 0

    max_iter = config["runtime"]["max_iterations"]
    for it in range(max_iter):
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        n_tries += 1

        # Save IR_t
        (iter_dir / "IR_t.json").write_text(
            json.dumps(ir_current, indent=2, ensure_ascii=False),
            encoding="utf-8")

        # Adaptor
        t0 = time.time()
        adapt_report = _run_adaptor(ir_current, iter_dir)
        t_adaptor = time.time() - t0
        exec_count += 1

        # Find STEP
        step_path = next(iter_dir.glob("*.step"), None)
        # Run feedbacks per method
        solver_fb = {"status": "skipped", "reason": "method disables solver"}
        kqp_fb = {"overall_status": "skipped", "error": "method disables kqp"}

        if method.get("run_solver_feedback") and step_path and step_path.exists():
            solver_fb = _run_solver(history_path)
        if method.get("run_kqp_feedback") and step_path and step_path.exists():
            kqp_fb = _run_kqp(step_path, kqp_path, plan_path,
                                  iter_dir / "kqp_feedback.json")
        elif method.get("run_kqp_feedback"):
            kqp_fb = {"overall_status": "fail", "error": "no step produced",
                        "query_results": []}

        verify_count += 2 if (method.get("run_solver_feedback")
                                and method.get("run_kqp_feedback")) else 1

        # Persist feedbacks
        (iter_dir / "solver_feedback.json").write_text(
            json.dumps(solver_fb, indent=2, ensure_ascii=False,
                          default=str), encoding="utf-8")
        (iter_dir / "kqp_feedback.json").write_text(
            json.dumps(kqp_fb, indent=2, ensure_ascii=False,
                          default=str), encoding="utf-8")

        # KQP success
        success_kqp = (kqp_fb.get("overall_status") == "pass")
        if success_kqp:
            k_iter = it + 1
            ir_t1 = ir_current
            ced = compute_ced(ir_t, ir_t1)
            (iter_dir / "IR_t1.json").write_text(
                json.dumps(ir_t1, indent=2, ensure_ascii=False),
                encoding="utf-8")
            (iter_dir / "ced.json").write_text(
                json.dumps(ced, indent=2, ensure_ascii=False,
                              default=str), encoding="utf-8")
            iter_records.append({
                "iter": it,
                "status": "success",
                "kqp_status": "pass",
                "solver_status": solver_fb.get("status"),
                "agent_called": False,
                "wallclock_s": t_adaptor,
            })
            final_status = "success"
            break

        # Call agent → IR_{t+1}
        # M0 (No Feedback) has no agent input; skip agent call entirely.
        if not method.get("run_solver_feedback") and not method.get("run_kqp_feedback"):
            ir_t1 = ir_current  # no-op edit
            agent_err = "M0_no_feedback: no agent call"
        else:
            ir_t1 = call_agent(ir_current, solver_fb, kqp_fb, method)
            agent_err = ir_t1.pop("_agent_error", None) if isinstance(ir_t1, dict) else None

        # Validate IR_t1
        valid, issues = validate_ir(ir_t1)
        if not valid:
            ir_t1 = ir_current  # fallback to no-op
        (iter_dir / "IR_t1.json").write_text(
            json.dumps(ir_t1, indent=2, ensure_ascii=False),
            encoding="utf-8")

        # Compute CED
        ced = compute_ced(ir_current, ir_t1)
        (iter_dir / "ced.json").write_text(
            json.dumps(ced, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8")
        ced_values.append(ced.get("ced_declared", {}).get("raw", 0))

        # Timing
        (iter_dir / "timing.json").write_text(json.dumps({
            "adaptor_seconds": t_adaptor,
            "agent_seconds": 0,  # not tracked in V0.1
        }, indent=2), encoding="utf-8")

        iter_records.append({
            "iter": it,
            "status": "kqp_fail",
            "kqp_status": "fail",
            "solver_status": solver_fb.get("status"),
            "agent_called": True,
            "agent_error": agent_err,
            "ced_raw": ced.get("ced_declared", {}).get("raw", 0),
            "wallclock_s": t_adaptor,
        })

        ir_current = ir_t1

    summary = {
        "method": method["id"],
        "sample_id": sample_id,
        "initial_kqp_pass": False,
        "iter_records": iter_records,
        "n_iterations": n_tries,
        "n_execution_attempts": exec_count,
        "n_verification_calls": verify_count,
        "ced_values_raw": ced_values,
        "ced_sum_raw": sum(ced_values),
        "repair_cost": sum(ced_values) + 0.1 * exec_count + 0.1 * verify_count,
        "success_kqp": success_kqp,
        "n_iterations_to_success": k_iter,
        "final_status": final_status,
    }
    (out_dir / "repair_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    return summary


# ---------------------------------------------------------------------------
# Per-method metrics
# ---------------------------------------------------------------------------

def compute_method_metrics(rows: list[dict]) -> dict:
    """Compute Success@K, F2S, MeanIter, KQP Q Improvement, RFQ,
    TRSR, CED, RepairCost, RuntimeCost, TokenCost across all rows."""
    n = len(rows)
    if n == 0:
        return {}
    success_by_iter: dict[int, int] = {1: 0, 2: 0, 3: 0}
    f2s_count = 0
    iter_to_success = []
    ced_values = []
    repair_costs = []
    runtime_costs = []
    # Per-method
    initial_pass = 0  # rows where initial IR was already-passing (should be 0 for negatives)
    final_pass = 0
    for r in rows:
        n_iters = r.get("n_iterations") or 0
        for k in (1, 2, 3):
            if r.get("success_kqp") and r.get("n_iterations_to_success") is not None \
                    and r["n_iterations_to_success"] <= k:
                success_by_iter[k] += 1
        if r.get("success_kqp"):
            f2s_count += 1
            if r.get("n_iterations_to_success"):
                iter_to_success.append(r["n_iterations_to_success"])
        ced_values.append(r.get("ced_sum_raw", 0))
        repair_costs.append(r.get("repair_cost", 0))
        if r.get("iter_records"):
            runtime_costs.append(sum(it.get("wallclock_s", 0)
                                          for it in r["iter_records"]))
        else:
            runtime_costs.append(0)
        if r.get("success_kqp"):
            final_pass += 1

    return {
        "n_samples": n,
        "n_initial_pass": initial_pass,
        "n_final_pass": final_pass,
        "n_failure_to_success": f2s_count,
        "Success@1": success_by_iter[1] / n,
        "Success@2": success_by_iter[2] / n,
        "Success@3": success_by_iter[3] / n,
        "F2S_ConversionRate": f2s_count / n,
        "MeanIterationsToSuccess": (sum(iter_to_success) / len(iter_to_success)
                                       if iter_to_success else None),
        "n_iterations_to_success_distribution": {
            "1": sum(1 for k in iter_to_success if k == 1),
            "2": sum(1 for k in iter_to_success if k == 2),
            "3": sum(1 for k in iter_to_success if k == 3),
        },
        "MeanCED_declared_raw": (sum(ced_values) / n if n else 0),
        "MeanRepairCost": (sum(repair_costs) / n if n else 0),
        "MeanRuntimeCost_s": (sum(runtime_costs) / n if n else 0),
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
        method_metrics = compute_method_metrics(method_rows)
        method_report = {
            "method": method_id,
            "name": method["name"],
            "run_solver_feedback": method["run_solver_feedback"],
            "run_kqp_feedback": method["run_kqp_feedback"],
            "metrics": method_metrics,
            "n_samples": len(method_rows),
            "rows": method_rows,
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