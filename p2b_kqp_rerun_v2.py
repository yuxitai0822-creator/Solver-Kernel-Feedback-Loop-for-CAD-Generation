"""Phase 2B KQP re-run for full benchmark.

Reads experiments/phase2b_full/pilot_results.json (v0.2 schema with
``sid`` / ``nid`` / ``method`` / ``layer``), loads the STEP file each
trial produced, and runs frame-only KQP bbox queries on it.

Output: experiments/phase2b_full/kqp_rerun.json  + a per-(method,
layer) summary printed at the end.
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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

OUT_DIR = ROOT / "experiments" / "phase2b_full"
RESULTS_PATH = OUT_DIR / "pilot_results.json"
KQP_PATH = OUT_DIR / "kqp_rerun.json"

results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
# Keep only successful step exports with a step_path
runnable = [r for r in results
            if r.get("step_export") and r.get("step_path")
            and Path(r["step_path"]).exists()
            and "error" not in r]
print(f"Total trials: {len(results)}  (runnable KQP: {len(runnable)})")

import collections
by_ml = collections.defaultdict(lambda: [0, 0])  # [n_total, n_step_export]

rerun_results = []
t0 = time.time()
for i, r in enumerate(runnable, 1):
    sid = r["sid"]
    sp = Path(r["step_path"])
    # KQP instance + design plan (frame)
    kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.2" / f"{sid}.kqp_instance.json"
    if not kqp_inst.exists():
        kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v6" / f"{sid}.kqp_instance.json"
    plan_p = ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
    if not plan_p.exists():
        plan_p = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    try:
        plan = json.loads(plan_p.read_text(encoding="utf-8"))
    except Exception as e:
        rerun_results.append({**r, "kqp_rerun": {"status": f"plan_load_failed: {e}"}})
        continue
    # OCCT load the STEP
    try:
        rr = STEPControl_Reader(); rr.ReadFile(str(sp)); rr.TransferRoots()
        shape = rr.OneShape()
    except Exception as e:
        rerun_results.append({**r, "kqp_rerun": {"status": f"occt_load_failed: {e}"}})
        continue
    f = plan.get("solid_bodies", [{}])[0].get("frame", {})
    frame = {"u_dir": f.get("u_dir", [1, 0, 0]),
              "v_dir": f.get("v_dir", [0, 1, 0]),
              "w_dir": f.get("w_dir", [0, 0, 1])}
    try:
        kqp = json.loads(kqp_inst.read_text(encoding="utf-8"))
    except Exception as e:
        rerun_results.append({**r, "kqp_rerun": {"status": f"kqp_load_failed: {e}"}})
        continue
    n_q = 0; n_fail = 0; failed = []
    for q in kqp.get("queries", []):
        if q.get("intent") != "bbox_size":
            continue
        n_q += 1
        try:
            res = qd.dispatch_query(shape, q, frame)
        except Exception as e:
            n_fail += 1
            failed.append(q.get("id"))
            continue
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
    by_ml[(r["method"], r["layer"])][0] += 1
    if n_fail > 0:
        by_ml[(r["method"], r["layer"])][1] += 1
    if i % 20 == 0 or i == len(runnable):
        KQP_PATH.write_text(json.dumps(rerun_results, indent=2, ensure_ascii=False, default=str),
                              encoding="utf-8")
        print(f"  [{i}/{len(runnable)}] {sid}/{r.get('nid')} {r['method']} "
              f"q={n_q} fail={n_fail} ({time.time()-t0:.0f}s)", flush=True)

KQP_PATH.write_text(json.dumps(rerun_results, indent=2, ensure_ascii=False, default=str),
                      encoding="utf-8")
print(f"\nRe-ran KQP on {len(rerun_results)} trials")
print()
print("Per (method, layer): n trials with at least one bbox failure")
print(f"  {'method':18s} {'layer':6s}  n  kqp_fail  rate")
for (m, l), (n, nf) in sorted(by_ml.items()):
    print(f"  {m:18s} {l:6s} {n:4d}  {nf:4d}     {nf/n*100:.1f}%")
