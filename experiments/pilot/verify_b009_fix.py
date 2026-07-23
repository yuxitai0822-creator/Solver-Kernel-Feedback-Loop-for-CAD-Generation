"""verify_b009_fix.py — Re-run KQP on all 50 clean samples (regression check)
and all 6 already-generated EX negatives to verify B-009 fix correctness.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))

CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"


def run_kqp_for_sample(step_path: Path, kqp_path: Path, plan_path: Path,
                         out_path: Path) -> dict:
    proc = subprocess.run(
        [CADQUERY_PYTHON, str(ROOT / "kqp" / "runner" / "run_kqp.py"),
          str(step_path), str(kqp_path), "--design-plan", str(plan_path),
          "-o", str(out_path)],
        capture_output=True, text=True, timeout=120,
        cwd=str(ROOT))
    if out_path.exists():
        try:
            return json.loads(out_path.read_text(encoding="utf-8"))
        except Exception as e:
            return {"error": f"parse: {e}", "stderr": proc.stderr[-200:]}
    return {"error": "no output", "stderr": proc.stderr[-200:]}


def summarize(method_dir: str, kqp_path: Path) -> dict:
    n_total = 0
    n_pass = 0
    n_fail = 0
    samples = []
    for sid in sorted(os.listdir(method_dir)):
        for nid in sorted(os.listdir(f"{method_dir}/{sid}")):
            sample_dir = f"{method_dir}/{sid}/{nid}"
            kqp_res_path = f"{sample_dir}/kqp_result.json"
            if not os.path.exists(kqp_res_path):
                continue
            n_total += 1
            kqp = json.load(open(kqp_res_path, encoding="utf-8"))
            status = kqp.get("overall_status", "?")
            if status == "pass": n_pass += 1
            elif status == "fail": n_fail += 1
            samples.append({"sid": sid, "nid": nid, "kqp": status})
    return {"n_total": n_total, "n_pass": n_pass, "n_fail": n_fail,
              "samples": samples}


def main():
    print("=" * 60)
    print("Verifying B-009 fix on 50 clean samples (regression check)")
    print("=" * 60)
    # Re-run KQP on all 50 clean samples
    clean_results = []
    samples = sorted(os.listdir("Reconstruction_results"))
    samples = [s for s in samples if not s.endswith(".json") and s != "frozen_v0.1"]
    for sid in samples:
        step_path = f"Reconstruction_results/{sid}/generated.step"
        if not os.path.exists(step_path):
            continue
        kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sid}.kqp_instance.json"
        plan_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
        out_path = Path("experiments/pilot/b009_clean_recheck") / sid / "kqp_result.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not kqp_inst.exists() or not plan_path.exists():
            print(f"  SKIP {sid} (missing KQP instance or plan)")
            continue
        kqp = run_kqp_for_sample(Path(step_path), kqp_inst, plan_path, out_path)
        status = kqp.get("overall_status", "?")
        clean_results.append((sid, status))
        if status not in ("pass",):
            print(f"  {sid}: status={status}")

    n_pass = sum(1 for _, s in clean_results if s == "pass")
    n_fail = sum(1 for _, s in clean_results if s == "fail")
    print(f"\nClean samples (post B-009 fix): pass={n_pass}, fail={n_fail}, total={len(clean_results)}")

    print()
    print("=" * 60)
    print("Verifying B-009 fix on EX perturbed samples")
    print("=" * 60)
    ex_results = []
    for sid in sorted(os.listdir("task5_negative_perturbation/perturbations")):
        for ex in ("ex1", "ex2"):
            ex_dir = Path("task5_negative_perturbation/perturbations") / sid / ex
            if not ex_dir.exists():
                continue
            step_path = ex_dir / "generated.step"
            if not step_path.exists():
                continue
            kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sid}.kqp_instance.json"
            plan_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
            out_path = Path("experiments/pilot/b009_ex_recheck") / sid / ex / "kqp_result.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            kqp = run_kqp_for_sample(step_path, kqp_inst, plan_path, out_path)
            status = kqp.get("overall_status", "?")
            ex_results.append((sid, ex, status))
            n_qs = sum(1 for q in kqp.get("query_results", []) if q.get("status") == "fail")
            n_qt = len(kqp.get("query_results", []))
            print(f"  {sid}/{ex}: status={status}  ({n_qs}/{n_qt} bbox queries failed)")

    n_pass = sum(1 for _, _, s in ex_results if s == "pass")
    n_fail = sum(1 for _, _, s in ex_results if s == "fail")
    print(f"\nEX samples (post B-009 fix): pass={n_pass}, fail={n_fail}, total={len(ex_results)}")


if __name__ == "__main__":
    main()
