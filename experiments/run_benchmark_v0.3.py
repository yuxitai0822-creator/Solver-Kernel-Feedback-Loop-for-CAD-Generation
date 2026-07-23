"""run_benchmark_v0.3.py — no-IR repair loop (Phase 2A Task A1.5).

The v0.2 pipeline was locked to the CAD IR schema.  v0.3 drops the IR
layer:  the LLM CAD Agent emits a raw cadquery Python script (no IR, no
patch), which is executed directly by cad_runtime.execute_cad_script.
S1–S4 stop rules are preserved; only the representation under repair
changes (script instead of IR).

Four methods, identical to v0.2:
  M0_NoFeedback, M1_SolverOnly, M2_KQPOnly, M3_SolverKQP

Per-method feedback injection (same semantics as v0.2):
  pipeline          always  (cad_runtime.executor result)
  solver_feedback   depends on method
  kqp_feedback      depends on method

The v0.2 frozen file lives at
``experiments/run_benchmark_v0.2_FROZEN.py`` and remains the legacy
IR-path.  This v0.3 file does NOT touch KQP, the IR compiler, or the
Reconstruction Engine (per Phase 2A R2).

CED calculation:  v0.2 used the IR-based CED.  v0.3 uses
``code2oper`` (Phase 2A Task A2) which parses the cadquery script via
AST and produces a structured operation list; ``compute_ced`` then
compares the two operation lists.  Until code2oper is implemented,
CED falls back to ``CED_text`` (Levenshtein over the script text)
per the R3 rule (CED_text is a mandatory fallback).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_runtime"))
sys.path.insert(0, str(ROOT / "cad_agent"))
sys.path.insert(0, str(ROOT / "experiments" / "b009_diagnosis"))

CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"

from cad_agent import call_cad_agent, make_no_change, make_repair
from cad_runtime import execute_cad_script

# Methods: each method controls which feedback channels are visible to
# the LLM in its prompt.  This matches v0.2's semantics: the four
# methods differ ONLY in which feedback channels are injected.
METHODS = {
    "M0_NoFeedback": {
        "name": "No (diagnostic) Feedback",
        "feedback_channels": [],  # the LLM sees only the DesignPlan
    },
    "M1_SolverOnly": {
        "name": "Solver Feedback Only",
        "feedback_channels": ["solver"],
    },
    "M2_KQPOnly": {
        "name": "KQP Feedback Only",
        "feedback_channels": ["kqp"],
    },
    "M3_SolverKQP": {
        "name": "Solver + KQP Feedback",
        "feedback_channels": ["solver", "kqp"],
    },
}


# Standard pipeline status fields (mirroring the IR-adaptor status block).
def _status_block(
    compile_status: bool,
    execution_status: bool,
    step_export: bool,
    occt_load: bool,
    runtime_error: str | None = None,
    step_path: str | None = None,
) -> dict:
    return {
        "compile_status": compile_status,
        "execution_status": execution_status,
        "step_export": step_export,
        "occt_load": occt_load,
        "runtime_error": runtime_error,
        "step_path": step_path,
    }


# CED helpers (text-only fallback while code2oper is pending).
def _normalize_script(s: str) -> str:
    import re
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + cost)
        prev = cur
    return prev[-1]


def _ced_text(s_t: str, s_t1: str) -> dict:
    """CED_text (mandatory fallback per R3)."""
    nt, nt1 = _normalize_script(s_t), _normalize_script(s_t1)
    if not nt and not nt1:
        return {"ced_text_normalized": 0.0, "ced_text_raw": 0,
                  "status": "empty_both"}
    if not nt or not nt1:
        return {"ced_text_normalized": 1.0, "ced_text_raw": max(len(nt), len(nt1)),
                  "status": "one_empty"}
    raw = _levenshtein(nt, nt1)
    norm = raw / max(len(nt), len(nt1))
    return {"ced_text_normalized": norm, "ced_text_raw": raw,
              "status": "ok"}


def _ced_declared(s_t: str, s_t1: str) -> dict:
    """CED_declared via code2oper.  Returns a parsed-failed placeholder
    until A2 is implemented; the caller should use CED_text as the
    primary signal.  Per R3, parse_coverage is reported."""
    try:
        from code2oper.parse import parse_cadquery_script
    except ImportError:
        return {"ced_declared": None, "parse_status": "code2oper_not_built",
                  "parse_coverage_unavailable": True}
    parsed_t = parse_cadquery_script(s_t)
    parsed_t1 = parse_cadquery_script(s_t1)
    if parsed_t is None or parsed_t1 is None:
        return {"ced_declared": None, "parse_status": "parse_failed",
                  "parse_coverage_unavailable": True}
    # The actual edit distance computation lives in compute_ced.py;
    # once Phase 2A Task A2.3 lands, the weighted op-edit-distance
    # implementation plugs in here.  Until then, report the count of
    # operations for transparency.
    return {"ced_declared": None, "parse_status": "parsed",
              "n_ops_t": len(parsed_t), "n_ops_t1": len(parsed_t1),
              "compute_pending": True}


# KQP runner (frozen at v0.1).  We use frame-axis projection (B-009 fix)
# via query_dispatcher; the dispatcher is patched in v0.2.
import importlib
def _import(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
qd = _import("qd_v0.1", ROOT / "kqp/runner/query_dispatcher.py")


def _run_kqp(step_path: Path, kqp_path: Path, plan_path: Path) -> dict:
    """Reuse the v0.1 query_dispatcher on the just-rendered STEP."""
    import sys
    sys.path.insert(0, str(ROOT / "kqp" / "runner"))
    from OCP.STEPControl import STEPControl_Reader
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import brepgprop_LinearProperties_s
    r = STEPControl_Reader()
    r.ReadFile(str(step_path))
    r.TransferRoots()
    shape = r.OneShape()
    bb = Bnd_Box(); BRepBndLib.Add_s(shape, bb)
    xmin, ymin, zmin, xmax, ymax, zmax = bb.CornerMin(), bb.CornerMax()
    world_spans = {"x": xmax - xmin, "y": ymax - ymin, "z": zmax - zmin}
    # Load KQP instance + DP frame
    kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    f = plan.get("solid_bodies", [{}])[0].get("frame", {})
    frame = {"u_dir": f.get("u_dir", [1, 0, 0]),
              "v_dir": f.get("v_dir", [0, 1, 0]),
              "w_dir": f.get("w_dir", [0, 0, 1])}
    out = {"queries": [], "overall_status": "pass"}
    n_pass = 0
    n_total = 0
    for q in kqp.get("queries", []):
        if q.get("intent") not in ("bbox_size", "cylinder_radius",
                                     "through_void_count", "body_count",
                                     "is_solid", "occt_valid", "symmetric_about_plane"):
            continue
        n_total += 1
        res = qd.dispatch_query(shape, q, frame)
        out["queries"].append(res)
        if res.get("status") == "pass":
            n_pass += 1
    if n_total and n_pass < n_total:
        out["overall_status"] = "fail"
    out["n_pass"] = n_pass
    out["n_total"] = n_total
    return out


# ---------------------------------------------------------------------------
# Per-sample loop
# ---------------------------------------------------------------------------

def run_one_sample_v0_3(method: dict, sample_id: str,
                          design_plan: dict, out_dir: Path,
                          config: dict) -> dict:
    """Single-sample no-IR repair loop.

    Mirrors run_one_sample v0.2 semantics; representation is
    CADScript (string) instead of IR.  Stop rules:
      S1 script == NO_CHANGE  (Agent emits no_change)
      S2 script_{t+1} == script_t (normalised text)
      S3 KQP success (all queries pass)
      S4 max_iter reached
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    max_iter = config.get("max_iterations", 3)

    iter_records = []
    script_t = ""  # start from no prior script
    iter_records_summary = []

    final_status = "max_iter"
    success = False
    n_iterations = 0
    k_iter_success = None
    input_tokens_total = 0
    output_tokens_total = 0
    sample_summary = None

    for it in range(max_iter):
        n_iterations = it + 1
        iter_dir = out_dir / f"iter_{it:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # Build the prompt's feedback payload.
        feedback = {}
        if it > 0 and iter_records:
            prev = iter_records[-1]
            if "solver" in method["feedback_channels"]:
                feedback["solver"] = prev.get("solver_feedback", {})
            if "kqp" in method["feedback_channels"]:
                feedback["kqp"] = prev.get("kqp_feedback", {})

        # Compose the agent input: design_plan + current script + feedback.
        agent_input = dict(design_plan)
        if script_t:
            agent_input["current_script"] = script_t
        if feedback:
            agent_input["feedback"] = feedback

        # Call the LLM.
        try:
            obj = call_cad_agent(agent_input, current_script=script_t,
                                  out_dir=str(iter_dir))
        except Exception as e:
            iter_records.append({"iter": it, "status": "agent_error",
                                      "error": str(e)})
            break

        if obj.get("action") == "no_change":
            # S1 stop: Agent says no repair needed.
            iter_records.append({"iter": it, "status": "S1_no_change",
                                      "agent_response": obj})
            final_status = "S1_no_change"
            break

        script_t1 = obj.get("script", "")
        if not script_t1:
            iter_records.append({"iter": it, "status": "no_script_in_response",
                                      "agent_response": obj})
            break

        # S2 stop: script_t1 == script_t (normalised).
        if script_t and _normalize_script(script_t1) == _normalize_script(script_t):
            iter_records.append({"iter": it, "status": "S2_script_unchanged",
                                      "script_t1": script_t1})
            final_status = "S2_script_unchanged"
            break

        # Run the script.
        exec_res = execute_cad_script(script_t1, iter_dir,
                                        out_step_name=f"{sample_id}.step")
        iter_records.append({"iter": it, "status": "S3_in_progress",
                                  "exec_res": exec_res,
                                  "script_t1": script_t1,
                                  "script_t1_len": len(script_t1)})

        if not exec_res["step_export"]:
            # Step export failed — continue or stop?
            # Treat as recoverable: keep going (the LLM may produce a
            # better script on next iter).
            script_t = script_t1
            continue

        # KQP check.
        kqp_inst_path = (ROOT / "kqp" / "outputs" / "compiler_v0.2"
                          / f"{sample_id}.kqp_instance.json")
        plan_path = (ROOT / "DesignPlan" / "compiler" / "instances_v6"
                        / f"{sample_id}.design_plan.json")
        if kqp_inst_path.exists() and plan_path.exists():
            kqp_res = _run_kqp(iter_dir / f"{sample_id}.step",
                                  kqp_inst_path, plan_path)
            iter_records[-1]["kqp_feedback"] = kqp_res
            if kqp_res.get("overall_status") == "pass":
                success = True
                k_iter_success = it + 1
                final_status = "S3_success"
                iter_records[-1]["status"] = "S3_success"
                break

        script_t = script_t1

    sample_summary = {
        "sample_id": sample_id,
        "method": method.get("id", method.get("name")),
        "n_iterations": n_iterations,
        "success": success,
        "n_iterations_to_success": k_iter_success,
        "stop_reason": final_status,
        "iter_records": iter_records,
    }
    return sample_summary


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", required=True, choices=list(METHODS.keys()))
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--out-root", default="experiments/results_v0.3")
    ap.add_argument("--clean-set", default="Reconstruction_results/clean_reconstruction_set.json")
    ap.add_argument("--plan-dir", default="DesignPlan/compiler/instances_v0.2")
    args = ap.parse_args()

    method = METHODS[args.method]
    method_id = args.method

    clean = json.loads(Path(args.clean_set).read_text(encoding="utf-8"))
    sids = [s["sample_id"] for s in clean.get("clean_samples", [])][:args.limit]

    out_root = Path(args.out_root) / method_id
    out_root.mkdir(parents=True, exist_ok=True)

    results = []
    for sid in sids:
        plan_path = Path(args.plan_dir) / f"{sid}.design_plan.json"
        if not plan_path.exists():
            print(f"  skip {sid} (no design plan)")
            continue
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        sample_dir = out_root / sid
        print(f"[{method_id}] {sid} -> {sample_dir}")
        res = run_one_sample_v0_3(method, sid, plan, sample_dir,
                                    {"max_iterations": 3})
        results.append(res)
    summary_path = out_root / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False),
                              encoding="utf-8")
    print(f"\nwrote {summary_path}  ({len(results)} samples)")


if __name__ == "__main__":
    main()
