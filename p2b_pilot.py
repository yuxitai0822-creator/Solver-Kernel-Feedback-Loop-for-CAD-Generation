"""Phase 2B Task B2.3 / B3 — pilot runner.

Runs M0, M1, M2, M3 on 30 selected samples (15 Type A + 15 EX2)
and records per-method pass/fail.  The agent uses the LLM (ZHIPU
glm-5.1) via cad_agent.call_cad_agent.

Output: experiments/phase2b_pilot_results.json
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path("D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_agent"))
sys.path.insert(0, str(ROOT / "cad_runtime"))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))
import importlib

# Reload modules to pick up Phase 2A fixes
for m in list(sys.modules):
    if m.startswith("cad_agent") or m.startswith("cad_runtime"):
        importlib.import_module(m)  # touch to ensure not stale

from cad_agent import call_cad_agent
from cad_runtime import execute_cad_script

# Load the v0.1 KQP dispatcher (frame-only — B-010 fix)
import importlib.util as iu
spec = iu.spec_from_file_location("qd", str(ROOT / "kqp" / "runner" / "query_dispatcher.py"))
qd = iu.module_from_spec(spec); spec.loader.exec_module(qd)

OUT_DIR = ROOT / "experiments" / "phase2b_pilot"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = OUT_DIR / "pilot_results.json"

SELECTION_PATH = ROOT / "experiments" / "phase2b_pilot_selection.json"
selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))

type_a_samples = selection["type_a_pick"]
ex2_samples = selection["ex2_pick"]


def get_design_plan(sid: str) -> dict:
    p = ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
    if not p.exists():
        p = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    return json.loads(p.read_text(encoding="utf-8"))


def run_method(method: str, sample: dict, perturbed_history_path: Path | None) -> dict:
    """Run a single (method, sample) trial.  Returns a result dict."""
    sid = sample["sample_id"]
    nid = sample["negative_id"]
    dp = get_design_plan(sid)
    out_dir = OUT_DIR / method / sid / nid
    out_dir.mkdir(parents=True, exist_ok=True)

    # M0: just the design plan.  M1/M2/M3: design plan + feedback
    # (we only have KQP feedback right now; solver feedback not wired).
    feedback = {}
    if method in ("M2_KQPOnly", "M3_SolverKQP"):
        # Run the agent with KQP feedback: for now, this requires a
        # previous STEP.  We approximate by running the LLM once with
        # the design plan, executing, and reading KQP.  Then a SECOND
        # LLM call with KQP feedback if the script needs fixing.
        # This is a 2-call loop.  For the pilot we do the first call
        # only and report the KQP result.
        pass

    obj = call_cad_agent(dp, current_script="", out_dir=str(out_dir))
    if obj.get("action") == "no_change":
        # Agent declared no change.  Save the empty result.
        return {
            "method": method, "sample_id": sid, "negative_id": nid,
            "agent_action": "no_change",
            "agent_status": obj.get("status", "?"),
        }
    script = obj.get("script", "")
    if not script:
        return {"method": method, "sample_id": sid, "negative_id": nid,
                  "agent_action": "no_script", "error": "no script in response"}
    (out_dir / "agent.py").write_text(script, encoding="utf-8")
    # Run the script.
    res = execute_cad_script(script, out_dir, out_step_name="generated.step")
    return {
        "method": method, "sample_id": sid, "negative_id": nid,
        "agent_action": "repair",
        "step_export": res.get("step_export", False),
        "compile_status": res.get("compile_status", False),
        "execution_status": res.get("execution_status", False),
        "occt_load": res.get("occt_load", False),
        "step_path": res.get("step_path"),
        "runtime_error": res.get("runtime_error"),
    }


def main():
    methods = ["M0_NoFeedback", "M1_SolverOnly", "M2_KQPOnly", "M3_SolverKQP"]
    all_results = []
    # Skip trials already in the result file
    existing_keys = set()
    try:
        for r in json.load(open(RESULTS_PATH, encoding='utf-8')):
            existing_keys.add((r.get('method'), r.get('sample_id'), r.get('negative_id')))
    except Exception:
        pass
    print(f'Already done: {len(existing_keys)} trials')
    for method in methods:
        for sample in type_a_samples + ex2_samples:
            sid = sample["sample_id"]
            nid = sample["negative_id"]
            label = "TypeA" if sample in type_a_samples else "EX2"
            if (method, sid, nid) in existing_keys:
                continue
            t0 = time.time()
            try:
                r = run_method(method, sample, None)
            except Exception as e:
                r = {"method": method, "sample_id": sid, "negative_id": nid,
                      "error": f"{type(e).__name__}: {str(e)[:200]}"}
            r["layer"] = label
            r["operator"] = sample.get("operator", "?")
            r["wallclock_sec"] = round(time.time() - t0, 2)
            all_results.append(r)
            # Save incrementally
            RESULTS_PATH.write_text(json.dumps(all_results, indent=2,
                                                ensure_ascii=False, default=str),
                                     encoding="utf-8")
            print(f"  [{method}] {sid}/{nid} ({label}): {r.get('agent_action', '?')}, "
                  f"step_export={r.get('step_export', '?')}, "
                  f"runtime={r['wallclock_sec']}s")

    # Summary
    print()
    print("=" * 60)
    print("Pilot summary")
    print("=" * 60)
    by_layer_method = {}
    for r in all_results:
        key = (r.get("layer", "?"), r.get("method", "?"))
        by_layer_method.setdefault(key, []).append(r)
    for (layer, method), rs in sorted(by_layer_method.items()):
        n_export = sum(1 for r in rs if r.get("step_export"))
        n_total = len(rs)
        print(f"  {layer:8s} {method:18s} {n_export}/{n_total} exported step")


if __name__ == "__main__":
    main()
