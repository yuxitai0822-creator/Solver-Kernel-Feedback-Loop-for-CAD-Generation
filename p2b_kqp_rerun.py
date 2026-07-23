"""Phase 2B B3 analysis: re-run KQP on M0 + M2 produced STEPS."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))
import importlib.util as iu

# Use the patched v0.1 dispatcher (frame-only KQP per B-010 fix)
spec = iu.spec_from_file_location("qd", str(ROOT / "kqp" / "runner" / "query_dispatcher.py"))
qd = iu.module_from_spec(spec); spec.loader.exec_module(qd)
import geometry_backend as gb
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

results = json.load(open(ROOT / "experiments" / "phase2b_pilot" / "pilot_results.json", encoding="utf-8"))
print(f"Total trials: {len(results)}")

# Re-run KQP on each M0 and M2 trial that has a step
rerun_results = []
for r in results:
    if r.get("method") not in ("M0_NoFeedback", "M2_KQPOnly"):
        continue
    if not r.get("step_path"):
        continue
    sp = Path(r["step_path"])
    if not sp.exists():
        continue
    sid = r["sample_id"]
    kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.2" / f"{sid}.kqp_instance.json"
    if not kqp_inst.exists():
        continue
    plan = ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
    if not plan.exists():
        plan = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    try:
        plan_data = json.loads(plan.read_text(encoding="utf-8"))
    except Exception:
        continue
    # Load STEP
    try:
        r2 = STEPControl_Reader(); r2.ReadFile(str(sp)); r2.TransferRoots()
        shape = r2.OneShape()
    except Exception:
        rerun_results.append({**r, "kqp_rerun": {"status": "occt_load_failed"}})
        continue
    f = plan_data.get("solid_bodies", [{}])[0].get("frame", {})
    frame = {"u_dir": f.get("u_dir", [1, 0, 0]),
              "v_dir": f.get("v_dir", [0, 1, 0]),
              "w_dir": f.get("w_dir", [0, 0, 1])}
    # Load KQP instance and run each query
    try:
        kqp = json.loads(kqp_inst.read_text(encoding="utf-8"))
    except Exception:
        continue
    n_q = 0
    n_fail = 0
    failed = []
    for q in kqp.get("queries", []):
        if q.get("intent") != "bbox_size":
            continue
        n_q += 1
        res = qd.dispatch_query(shape, q, frame)
        if res.get("status") != "pass":
            n_fail += 1
            failed.append(q.get("id"))
    rerun_results.append({
        **r, "kqp_rerun": {
            "n_bbox_queries": n_q,
            "n_bbox_fail": n_fail,
            "failed_query_ids": failed,
        }
    })
    # Save incrementally
    out_path = ROOT / "experiments" / "phase2b_pilot" / "kqp_rerun.json"
    out_path.write_text(json.dumps(rerun_results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"Re-ran KQP on {len(rerun_results)} M0+M2 trials")
# Summary by (method, layer): how many trials had at least one bbox failure
import collections
by_ml = collections.defaultdict(lambda: [0, 0])  # [n, n_kqp_failed]
for r in rerun_results:
    k = (r["method"], r["layer"])
    by_ml[k][0] += 1
    if r.get("kqp_rerun", {}).get("n_bbox_fail", 0) > 0:
        by_ml[k][1] += 1
print()
print("Per (method, layer): n trials with at least one bbox failure")
for (m, l), (n, nf) in sorted(by_ml.items()):
    print(f"  {m:18s} {l:6s} n={n:2d} bbox_fail={nf:2d} rate={nf/n*100:.0f}%")
