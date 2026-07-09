"""repair_loop.py — Single-sample repair loop.

Pipeline per iteration:
  1. Take IR_t (or initial IR from design plan)
  2. Run Adaptor → STEP
  3. Run Solver Feedback → solver_feedback
  4. Run KQP Feedback → kqp_feedback
  5. Compute CED(IR_t, IR_{t+1}) — but first, get IR_{t+1}:
       - call_agent(IR_t, solver_feedback, kqp_feedback) → IR_{t+1}
  6. Save iteration to disk (IR_t, IR_{t+1}, CED, solver, kqp, step)
  7. Repeat until solver_feedback.passes and kqp_feedback.passes, or N

Final outputs per sample:
  repair_iteration_NN/IR_t.json   IR_{t+1}.json   ced.json
                   solver_feedback.json  kqp_feedback.json
                   generated.step
  repair_summary.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
sys.path.insert(0, str(ROOT / "cad_ir" / "adaptor"))
sys.path.insert(0, str(ROOT / "cad_edit_distance"))

import importlib
_validate_mod = importlib.import_module("cad_ir.validator.validator")
validate = _validate_mod.validate

_adapt_mod = importlib.import_module("cad_ir.adaptor.adapter")
adapt = _adapt_mod.adapt

_ced_mod = importlib.import_module("cad_edit_distance.compute_ced")
compute_all = _ced_mod.compute_all

_agent_mod = importlib.import_module("cad_repair_loop.llm_agent")
call_agent = _agent_mod.call_agent


def run_solver_feedback_on_step(step_path: Path) -> dict:
    """Run the (frozen) Freecad Solver Feedback v0.1 on a STEP file.

    For Phase-4 the solver feedback is optional; we return a
    'skipped' marker when FreeCAD is unavailable or the STEP is
    malformed.  The repair loop still runs end-to-end via KQP feedback.
    """
    try:
        sys.path.insert(0, str(ROOT / "Freecadsolver_feedback" / "core"))
        from Freecadsolver_feedback.core.solver_runner import (
            run_solver_from_history as fc_run,
        )
    except Exception:
        return {"status": "skipped",
                "note": "Freecad Solver Feedback not loadable"}

    # We don't have a history JSON; use a minimal stub
    return {"status": "skipped",
              "note": "Freecad Solver Feedback requires history JSON; "
                       "Phase 4 loop uses KQP feedback only"}


def run_kqp_feedback(step_path: Path, design_plan: dict) -> dict:
    """Run the (frozen) KQP runner on a STEP file vs the design plan.

    Returns a minimal dict compatible with the repair loop:
      * query_results: list of {query_id, intent, status, expected, actual, tolerance}
      * overall_status: 'pass' | 'fail'
    """
    try:
        sys.path.insert(0, str(ROOT / "kqp" / "runner"))
        from kqp.runner.run_kqp import run_kqp as kqp_run
    except Exception as e:
        return {"overall_status": "unknown",
                "query_results": [],
                "error": f"KQP not loadable: {e}"}

    # Build a minimal kqp_instance from design_plan
    sample_id = design_plan.get("solid_bodies", [{}])[0].get(
        "name", design_plan.get("sample_id", "unknown"))
    kqp_dir = ROOT / "kqp" / "outputs" / "compiler_v0.1"
    kqp_path = kqp_dir / f"{sample_id}.kqp_instance.json"
    if not kqp_path.exists():
        return {"overall_status": "unknown", "query_results": [],
                "error": f"no KQP instance for {sample_id}"}

    try:
        out_path = Path("/tmp/kqp_out.json")
        rc = kqp_run(step_path, kqp_path, design_plan, out_path)
        if out_path.exists():
            kqp = json.loads(out_path.read_text(encoding="utf-8"))
        else:
            kqp = {"overall_status": "fail",
                    "query_results": [],
                    "summary": {"failed_queries": 1}}
    except Exception as e:
        return {"overall_status": "fail", "query_results": [],
                "error": str(e)}
    return kqp


def run_repair_loop(initial_ir: dict,
                       design_plan: dict,
                       out_dir: Path,
                       *,
                       max_iterations: int = 5,
                       agent_mode: str = "auto") -> dict:
    """Run repair loop until success or max_iterations.

    Returns dict with per-iteration records and a RepairCost summary.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ir_t = initial_ir
    iter_records = []
    ced_values = []
    exec_count = 0
    verify_count = 0

    for it in range(max_iterations):
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        (iter_dir / "IR_t.json").write_text(
            json.dumps(ir_t, indent=2, ensure_ascii=False),
            encoding="utf-8")

        # Step 1: validate IR
        val = validate(ir_t)
        if val["overall"] != "pass":
            (iter_dir / "solver_feedback.json").write_text(
                json.dumps({"status": "validation_failed",
                             "issues": val["schema_issues"] + val["semantic_issues"]},
                            indent=2),
                encoding="utf-8")
            iter_records.append({"iter": it, "status": "invalid_ir"})
            break

        # Step 2: run adaptor
        try:
            adapt_report = adapt(ir_t, iter_dir, sample_id=ir_t.get("sample_id"))
        except Exception as e:
            adapt_report = {"adapter_status": "fail",
                              "warnings": [str(e)]}
            (iter_dir / "adapter_report.json").write_text(
                json.dumps(adapt_report, indent=2),
                encoding="utf-8")
        exec_count += 1
        step_path = iter_dir / f"{ir_t.get('sample_id')}.step"
        if not step_path.exists():
            # Search for any .step in iter_dir
            candidates = list(iter_dir.glob("*.step"))
            step_path = candidates[0] if candidates else None

        # Step 3: solver feedback
        sf_path = iter_dir / "solver_feedback.json"
        solver_fb = {"status": "skipped", "note": "FreeCAD not active in Phase 4"}
        sf_path.write_text(json.dumps(solver_fb, indent=2), encoding="utf-8")
        verify_count += 1

        # Step 4: KQP feedback
        kf_path = iter_dir / "kqp_feedback.json"
        if step_path and step_path.exists():
            kqp_fb = run_kqp_feedback(step_path, design_plan)
        else:
            kqp_fb = {"overall_status": "fail",
                       "query_results": [],
                       "error": "no step produced"}
        kf_path.write_text(json.dumps(kqp_fb, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        verify_count += 1

        # Decide termination
        kqp_pass = kqp_fb.get("overall_status") == "pass"
        sf_pass = solver_fb.get("solve_status") in ("fully_constrained",
                                                       "pass", "redundant", "warning")
        iter_records.append({"iter": it, "status": "kqp_pass" if kqp_pass else "kqp_fail",
                              "solver_status": solver_fb.get("status"),
                              "kqp_status": kqp_fb.get("overall_status")})
        if kqp_pass and sf_pass:
            ir_t1 = ir_t  # no change needed
            ced_result = compute_all(ir_t, ir_t1)
            (iter_dir / "IR_t1.json").write_text(json.dumps(ir_t1, indent=2,
                                                                ensure_ascii=False),
                                                   encoding="utf-8")
            (iter_dir / "ced.json").write_text(json.dumps(ced_result, indent=2,
                                                             ensure_ascii=False),
                                                 encoding="utf-8")
            break

        # Step 5: call LLM agent → IR_t1
        try:
            ir_t1 = call_agent(design_plan, ir_t, solver_fb, kqp_fb,
                                  mode=agent_mode)
        except Exception as e:
            ir_t1 = ir_t
            (iter_dir / "agent_error.txt").write_text(str(e),
                                                       encoding="utf-8")
            iter_records[-1]["agent_error"] = str(e)
            break

        # Step 6: validate IR_t1
        val1 = validate(ir_t1)
        if val1["overall"] != "pass":
            # Try to fall back to a no-op IR
            ir_t1 = ir_t
        (iter_dir / "IR_t1.json").write_text(json.dumps(ir_t1, indent=2,
                                                            ensure_ascii=False),
                                                encoding="utf-8")

        # Step 7: compute CED
        ced_result = compute_all(ir_t, ir_t1)
        (iter_dir / "ced.json").write_text(json.dumps(ced_result, indent=2,
                                                         ensure_ascii=False),
                                             encoding="utf-8")
        ced_values.append(ced_result["ced_declared"]["raw"])

        ir_t = ir_t1

    summary = {
        "sample_id": ir_t.get("sample_id"),
        "iterations": iter_records,
        "n_iterations": len(iter_records),
        "n_execution_attempts": exec_count,
        "n_verification_calls": verify_count,
        "ced_values_raw": ced_values,
        "ced_sum_raw": sum(ced_values),
        "repair_cost": sum(ced_values)
                        + 0.1 * exec_count
                        + 0.1 * verify_count,
        "final_status": iter_records[-1]["status"] if iter_records else "no_iter",
    }
    (out_dir / "repair_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    return summary