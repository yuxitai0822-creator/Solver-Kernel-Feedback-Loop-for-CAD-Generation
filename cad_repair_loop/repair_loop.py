"""repair_loop.py — Single-sample repair loop.

Pipeline per iteration:
  1. Take IR_t (or initial IR from design plan)
  2. Run Adaptor → STEP
  3. Run Solver Feedback → solver_feedback
       (uses original history JSON + FreeCAD Sketcher when available)
  4. Run KQP Feedback → kqp_feedback
  5. Compute CED(IR_t, IR_{t+1}) — but first, get IR_{t+1}:
       - call_agent(IR_t, solver_feedback, kqp_feedback) → IR_{t+1}
  6. Save iteration to disk (IR_t, IR_{t+1}, CED, solver, kqp, step)
  7. Repeat until both feedbacks pass, or N

Final outputs per sample:
  repair_iteration_NN/IR_t.json   IR_{t+1}.json   ced.json
                   solver_feedback.json  kqp_feedback.json
                   generated.step
  repair_summary.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
sys.path.insert(0, str(ROOT / "cad_edit_distance"))

import importlib
_validate_mod = importlib.import_module("cad_ir.validator.validator")
validate = _validate_mod.validate

_ced_mod = importlib.import_module("cad_edit_distance.compute_ced")
compute_all = _ced_mod.compute_all

_agent_mod = importlib.import_module("cad_repair_loop.llm_agent")
call_agent = _agent_mod.call_agent


# In-process Adaptor reference (used when running in cad_subproject1
# env which has cadquery available).  When running in freecad_sketcher
# env, we use the subprocess_bridge instead.
try:
    _adapt_mod = importlib.import_module("cad_ir.adaptor.adapter")
    _inproc_adapt = _adapt_mod.adapt
    _HAS_INPROC_ADAPTOR = True
except Exception:
    _inproc_adapt = None
    _HAS_INPROC_ADAPTOR = False


def _adapt(ir: dict, iter_dir: Path, sample_id: str) -> dict:
    """Adaptor dispatch:
       * in-process with cadquery env's python if cadquery is importable;
       * subprocess via cad_subproject1 python otherwise.

    Always pass python_exe=cadquery python when cadquery is not in
    sys.path so the generated script runs in an env with cadquery.
    """
    from cad_repair_loop.subprocess_bridge import CADQUERY_PYTHON

    if _HAS_INPROC_ADAPTOR:
        try:
            return _inproc_adapt(ir, iter_dir, sample_id=sample_id,
                                  python_exe=CADQUERY_PYTHON)
        except Exception as e:
            return {"sample_id": sample_id, "adapter_status": "fail",
                    "warnings": [f"in-process adaptor failed: {type(e).__name__}: {e}"]}
    # Subprocess path
    from cad_repair_loop.subprocess_bridge import run_adaptor_subprocess
    return run_adaptor_subprocess(ir, iter_dir)


# ---------------------------------------------------------------------------
# KQP feedback (correctly calls run_kqp(step_path, kqp_dict, plan_dict))
# ---------------------------------------------------------------------------

def _resolve_kqp_artifact_paths(sample_id: str) -> tuple[Path | None, Path | None]:
    """Resolve the on-disk paths of KQP instance + DesignPlan v0.6 for a sample."""
    if not sample_id:
        return None, None
    kqp_path = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sample_id}.kqp_instance.json"
    plan_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sample_id}.design_plan.json"
    if not kqp_path.exists():
        kqp_path = None
    if not plan_path.exists():
        plan_path = None
    return kqp_path, plan_path


def run_kqp_feedback(step_path: Path, design_plan: dict,
                      *, output_path: Path | None = None) -> dict:
    """Run the (frozen) KQP runner on a STEP file + KQP instance + DesignPlan.

    Routing:
      * in-process if `kqp.runner.run_kqp.run_kqp` is importable
        (cad_subproject1 env)
      * via subprocess in `cad_subproject1` env otherwise
        (freecad_sketcher env — FreeCAD only)

    Requires the on-disk KQP instance and DesignPlan JSON.  If they're
    missing, returns `overall_status: unknown`.
    """
    sample_id = (design_plan.get("sample_id", "")
                  or design_plan.get("source_component_name", "")
                  or (design_plan.get("solid_bodies", [{}])[0]
                       .get("name", "")
                       if design_plan.get("solid_bodies") else "")
                  or "")

    kqp_path, plan_path = _resolve_kqp_artifact_paths(sample_id)

    if not step_path or not step_path.exists():
        return {"overall_status": "fail", "query_results": [],
                "error": "no step_path"}

    if not kqp_path:
        return {"overall_status": "unknown",
                "query_results": [],
                "error": f"no KQP instance for {sample_id}"}

    # Try in-process first
    try:
        sys.path.insert(0, str(ROOT / "kqp" / "runner"))
        from kqp.runner.run_kqp import run_kqp as kqp_run
        if plan_path and plan_path.exists():
            plan_dict = json.loads(plan_path.read_text(encoding="utf-8"))
        else:
            plan_dict = {"solid_bodies": [{"name": sample_id,
                                             "frame": {"u_dir": [1,0,0],
                                                        "v_dir": [0,1,0],
                                                        "w_dir": [0,0,1]}}],
                          "sample_id": sample_id}
        kqp_dict = json.loads(kqp_path.read_text(encoding="utf-8"))
        return kqp_run(step_path, kqp_dict, plan_dict)
    except Exception as e:
        # In-process failed (e.g. OCP missing in freecad_sketcher env);
        # fall back to subprocess.
        if output_path is None:
            output_path = step_path.parent / "kqp_feedback_subprocess.json"
        try:
            from cad_repair_loop.subprocess_bridge import run_kqp_subprocess
            return run_kqp_subprocess(step_path, kqp_path, plan_path or Path(""), output_path)
        except Exception as e2:
            return {"overall_status": "fail",
                    "query_results": [],
                    "error": f"in-process: {type(e).__name__}: {e}; "
                              f"subprocess: {type(e2).__name__}: {e2}"}


# ---------------------------------------------------------------------------
# Solver feedback (FreeCAD Sketcher)
#
# Solver feedback requires a sketch defined as FreeCAD geometry +
# constraints.  Per iteration, we re-construct the sketch from the
# ORIGINAL Fusion360 history JSON (the source of truth), since perturbed
# IRs do not carry an explicit sketch specification.  If the history
# JSON is missing (e.g. for synthetic LLM-generated IRs), we skip.
# ---------------------------------------------------------------------------

def run_solver_feedback(step_path_or_ir: dict | Path | None = None,
                          *, history_path: Path | None = None,
                          sample_id: str | None = None) -> dict:
    """Run the (frozen) FreeCAD Solver Feedback v0.1.

    Three input modes:
      * `step_path_or_ir` is a Path  → load original history from
        Reconstruction_results/<sample_id>/input_history.json
      * `history_path` is provided    → load that history directly
      * `step_path_or_ir` is a dict   → caller-provided history JSON

    V0.1 limitation: FreeCAD solver feedback is bound to the Fusion360
    history JSON structure.  Perturbed IRs that change op_type still reuse
    the ORIGINAL history — V0.2 should construct a FreeCAD sketch from the
    perturbed IR itself (requires a FreeCAD-adaptor, deferred).
    """
    # Resolve history JSON path
    if history_path is None and sample_id is not None:
        history_path = (ROOT / "Reconstruction_results" / sample_id
                          / "input_history.json")
        if not history_path.exists():
            history_path = None

    if history_path is None:
        # Try to recover the source sample_id from the IR's sample_id
        # (and check for a matching entry in the clean_reconstruction_set)
        return {"status": "skipped",
                "reason": "no history JSON available for this sample"}

    if not history_path.exists():
        return {"status": "skipped",
                "reason": f"history_path missing: {history_path}"}

    try:
        sys.path.insert(0, str(ROOT / "Freecadsolver_feedback" / "core"))
        from Freecadsolver_feedback.core.solver_runner import (
            run_solver_from_history)
        from Freecadsolver_feedback.core.recompute_runner import (
            run_recompute_from_state)
        from Freecadsolver_feedback.core.diagnostic_normalizer import (
            normalize_solve, normalize_recompute)
    except Exception as e:
        return {"status": "skipped",
                "reason": f"FreeCAD solver feedback not importable: {e}"}

    try:
        history = json.loads(history_path.read_text(encoding="utf-8"))
        raw = run_solver_from_history(history)
        rc = run_recompute_from_state(raw)
        normalized = normalize_solve(raw)
        # Make sure the keys we need are present
        normalized["return_code"] = raw.get("solve_return_code", 0)
        normalized["dof"] = raw.get("dof", 0)
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
            "non_linear": raw.get("non_linear_constraint_ids", []),
            "deleted_entities": raw.get("deleted_entities_referenced", []),
            "registry": raw.get("registry", {}),
        }
    except Exception as e:
        import traceback
        return {"status": "skipped",
                "reason": f"FreeCAD solver feedback failed: {type(e).__name__}: {e}",
                "traceback": traceback.format_exc()[-500:]}


# ---------------------------------------------------------------------------
# Top-level loop
# ---------------------------------------------------------------------------

def run_repair_loop(initial_ir: dict,
                       design_plan: dict,
                       out_dir: Path,
                       *,
                       history_path: Path | None = None,
                       use_solver_feedback: bool = True,
                       max_iterations: int = 5,
                       agent_mode: str = "auto",
                       success_kqp: bool = True,
                       success_solver: bool = False) -> dict:
    """Run repair loop until success or max_iterations.

    Args:
      initial_ir     : starting IR (cad_ir_v0.1 dict)
      design_plan    : original DesignPlan v0.6 dict
      out_dir        : directory for per-iteration artifacts
      history_path   : Fusion360 history JSON for FreeCAD solver feedback
                       (if None, tries to auto-discover from sample_id)
      use_solver_feedback : if False, skip solver feedback entirely
      max_iterations : maximum loop iterations
      agent_mode     : 'auto' / 'online' / 'offline' (LLM agent backend)
      success_kqp    : require KQP pass to terminate
      success_solver : require Solver pass to terminate (rare since
                       most IRs reuse the original sketch)
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ir_t = initial_ir
    iter_records = []
    ced_values = []
    exec_count = 0
    verify_count = 0

    sample_id = ir_t.get("sample_id", "unknown")
    if history_path is None:
        # Auto-discover the original history JSON
        candidate = ROOT / "Reconstruction_results" / sample_id / "input_history.json"
        if candidate.exists():
            history_path = candidate

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

        # Step 2: run adaptor (subprocess in cad_subproject1)
        try:
            adapt_report = _adapt(ir_t, iter_dir, sample_id=sample_id)
            # Persist the report so user can inspect
            (iter_dir / "adapter_report.json").write_text(
                json.dumps(adapt_report, indent=2, ensure_ascii=False),
                encoding="utf-8")
        except Exception as e:
            import traceback
            adapt_report = {"adapter_status": "fail",
                              "warnings": [f"{type(e).__name__}: {e}"],
                              "traceback": traceback.format_exc()[-500:]}
            (iter_dir / "adapter_report.json").write_text(
                json.dumps(adapt_report, indent=2, ensure_ascii=False),
                encoding="utf-8")
        exec_count += 1
        step_path = iter_dir / f"{sample_id}.step"
        if not step_path.exists():
            candidates = list(iter_dir.glob("*.step"))
            step_path = candidates[0] if candidates else None

        # Step 3: solver feedback (FreeCAD)
        sf_path = iter_dir / "solver_feedback.json"
        if use_solver_feedback and history_path is not None:
            solver_fb = run_solver_feedback(
                history_path=history_path, sample_id=sample_id)
        else:
            solver_fb = {"status": "skipped",
                         "reason": "no history_path available" if history_path is None
                          else "use_solver_feedback=False"}
        sf_path.write_text(json.dumps(solver_fb, indent=2,
                                       ensure_ascii=False),
                            encoding="utf-8")
        verify_count += 1

        # Step 4: KQP feedback (frozen kqp/runner)
        kf_path = iter_dir / "kqp_feedback.json"
        if step_path and step_path.exists():
            # Use real DesignPlan from instances_v6 if available
            real_design_plan = design_plan
            plan_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sample_id}.design_plan.json"
            if plan_path.exists():
                real_design_plan = json.loads(plan_path.read_text(encoding="utf-8"))
            kqp_fb = run_kqp_feedback(step_path, real_design_plan)
        else:
            kqp_fb = {"overall_status": "fail",
                       "query_results": [],
                       "error": "no step produced"}
        kf_path.write_text(json.dumps(kqp_fb, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        verify_count += 1

        # Decide termination
        kqp_pass = kqp_fb.get("overall_status") == "pass"
        sf_pass = (solver_fb.get("status") == "ran"
                    and solver_fb.get("solve", {}).get("solve_status")
                        in ("fully_constrained", "over_constrained", "redundant"))

        cond_kqp = (not success_kqp) or kqp_pass
        cond_solver = (not success_solver) or sf_pass

        iter_records.append({
            "iter": it,
            "status": ("success" if cond_kqp and cond_solver
                        else ("kqp_fail" if not kqp_pass else "solver_fail")),
            "kqp_status": kqp_fb.get("overall_status"),
            "solver_status": (solver_fb.get("solve", {}).get("solve_status")
                                if solver_fb.get("status") == "ran" else "skipped"),
        })
        if cond_kqp and cond_solver:
            # No change needed; record and break
            ir_t1 = ir_t
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
            (iter_dir / "agent_error.txt").write_text(
                f"{type(e).__name__}: {e}\n"
                "Hint: in offline mode this is unreachable; in online mode "
                "this may be a network timeout — agent retry policy applied.",
                encoding="utf-8")
            iter_records[-1]["agent_error"] = f"{type(e).__name__}: {e}"
            break

        # Step 6: validate IR_t1
        val1 = validate(ir_t1)
        if val1["overall"] != "pass":
            ir_t1 = ir_t  # fallback to no-op
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
        "sample_id": sample_id,
        "iter_records": iter_records,
        "n_iterations": len(iter_records),
        "n_execution_attempts": exec_count,
        "n_verification_calls": verify_count,
        "ced_values_raw": ced_values,
        "ced_sum_raw": sum(ced_values),
        "repair_cost": sum(ced_values)
                        + 0.1 * exec_count
                        + 0.1 * verify_count,
        "final_status": iter_records[-1]["status"] if iter_records else "no_iter",
        "use_solver_feedback": use_solver_feedback,
        "agent_mode": agent_mode,
        "history_path_resolved": (str(history_path)
                                   if history_path else None),
    }
    (out_dir / "repair_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    return summary