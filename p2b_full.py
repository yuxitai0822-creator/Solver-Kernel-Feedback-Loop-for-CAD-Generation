"""Phase 2B Full Benchmark — uses DeepSeek via OpenAI SDK."""
import importlib.util as iu
import json
import os
import sys
import time
from pathlib import Path

# Use the script's location so WSL/Bash path conversion does not munge
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))

spec = iu.spec_from_file_location("agent_v2", str(ROOT / "cad_agent" / "agent_v2.py"))
agent_v2 = iu.module_from_spec(spec); spec.loader.exec_module(agent_v2)

spec = iu.spec_from_file_location("qd", str(ROOT / "kqp" / "runner" / "query_dispatcher.py"))
qd = iu.module_from_spec(spec); spec.loader.exec_module(qd)
import geometry_backend as gb
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

from cad_runtime import execute_cad_script


OUT_DIR = ROOT / "experiments" / "phase2b_full"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = OUT_DIR / "pilot_results.json"

# Get ALL Type A + EX2 samples
all_type_a = []
all_ex2 = []
for sid_dir in (ROOT / "task5_negative_perturbation/perturbations").iterdir():
    sid = sid_dir.name
    for nid_dir in sid_dir.iterdir():
        nid = nid_dir.name
        meta_path = nid_dir / "perturbation_meta.json"
        if not meta_path.exists():
            continue
        meta = json.load(open(meta_path, encoding="utf-8"))
        # EX2 uses the ``operator`` key; Type A uses ``operator_input_name``.
        op = meta.get("operator_input_name") or meta.get("operator") or "?"
        if op.startswith("E") and not op.startswith("EX"):
            all_type_a.append((sid, nid, op))
        elif op == "EX2_coordinate_flip":
            all_ex2.append((sid, nid, op))

print(f"Total samples: TypeA={len(all_type_a)}, EX2={len(all_ex2)}")
print(f"Total trials x 4 methods: {(len(all_type_a)+len(all_ex2))*4}")

methods = ["M0_NoFeedback", "M1_SolverOnly", "M2_KQPOnly", "M3_SolverKQP"]


def get_plan(sid):
    p = ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
    if not p.exists():
        p = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    return json.load(open(p, encoding="utf-8"))


def run_trial(method, sid, nid, layer):
    plan = get_plan(sid)
    out_dir = OUT_DIR / method / sid / nid
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        obj = agent_v2.call_cad_agent(plan, current_script="", out_dir=str(out_dir))
        if obj.get("action") == "no_change":
            return {"method": method, "sid": sid, "nid": nid, "layer": layer,
                    "agent_action": "no_change", "wallclock": round(time.time()-t0, 2)}
        script = obj.get("script", "")
        if not script:
            return {"method": method, "sid": sid, "nid": nid, "layer": layer,
                    "agent_action": "no_script", "wallclock": round(time.time()-t0, 2)}
        (out_dir / "agent.py").write_text(script, encoding="utf-8")
        res = execute_cad_script(script, out_dir, out_step_name="generated.step")
        return {"method": method, "sid": sid, "nid": nid, "layer": layer,
                "agent_action": "repair",
                "step_export": res.get("step_export", False),
                "occt_load": res.get("occt_load", False),
                "runtime_error": res.get("runtime_error"),
                "step_path": res.get("step_path"),
                "wallclock": round(time.time()-t0, 2)}
    except Exception as e:
        return {"method": method, "sid": sid, "nid": nid, "layer": layer,
                "error": f"{type(e).__name__}: {str(e)[:200]}",
                "wallclock": round(time.time()-t0, 2)}


def main():
    all_results = []
    # Only treat a trial as "done" if it produced a real result.
    # Trials that errored (no DEEPSEEK key, network blip, etc.) stay in
    # the file for the audit trail but will be re-run.
    existing_keys = set()
    if RESULTS_PATH.exists():
        try:
            for r in json.load(open(RESULTS_PATH, encoding="utf-8")):
                all_results.append(r)
                if "error" not in r:
                    existing_keys.add((r.get("method"), r.get("sid"), r.get("nid")))
        except Exception:
            pass
    n_errored = sum(1 for r in all_results if "error" in r)
    print(f"Already done (non-error): {len(existing_keys)} trials  "
          f"({n_errored} errored will be retried)")
    trials = ([(s, n, o, "TypeA") for s, n, o in all_type_a] +
              [(s, n, o, "EX2") for s, n, o in all_ex2])
    print(f"Total trials to run: {len(trials)} x 4 methods = {len(trials)*4}")
    n_done = 0
    t_start = time.time()
    try:
        for sid, nid, op, layer in trials:
            for method in methods:
                if (method, sid, nid) in existing_keys:
                    continue
                t0 = time.time()
                try:
                    r = run_trial(method, sid, nid, layer)
                except KeyboardInterrupt:
                    raise
                except BaseException as e:  # noqa: BLE001
                    # Catch absolutely anything so the run does not die
                    # mid-batch from a stray exception (e.g. an unhandled
                    # openai error after our retry loop).  Record it and
                    # keep going.
                    r = {"method": method, "sid": sid, "nid": nid, "layer": layer,
                         "operator": op,
                         "error": f"runner_crash: {type(e).__name__}: {str(e)[:200]}",
                         "wallclock": round(time.time() - t0, 2)}
                r["operator"] = op
                if "wallclock" not in r:
                    r["wallclock"] = round(time.time() - t0, 2)
                all_results.append(r)
                n_done += 1
                # Write atomically: write to .tmp, then rename.  This way
                # a power loss / network drop on the user's side can only
                # lose at most one trial, and the file is never half-
                # written.
                tmp_path = RESULTS_PATH.with_suffix(".json.tmp")
                tmp_path.write_text(
                    json.dumps(all_results, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8")
                os.replace(tmp_path, RESULTS_PATH)
                elapsed = round(time.time() - t_start, 1)
                print(f"  [{n_done}] {method:18s} {layer:5s} {sid}/{nid} "
                      f"({op}): step_export={r.get('step_export', '?')} "
                      f"err={r.get('runtime_error') or r.get('error', '-') or '-'} "
                      f"({r['wallclock']}s) [cumul {elapsed}s]", flush=True)
    except KeyboardInterrupt:
        # Persist everything we have so far, then bail.
        try:
            RESULTS_PATH.write_text(
                json.dumps(all_results, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8")
        except Exception:
            pass
        print(f"\n*** KeyboardInterrupt ***  Persisted {len(all_results)} trials.  "
              f"Re-run to resume.")
        return
    print(f"\nDone. {len(all_results)} trials total.")


if __name__ == "__main__":
    main()
