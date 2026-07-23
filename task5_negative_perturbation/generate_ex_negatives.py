"""generate_ex_negatives.py — Generate EX1/EX2 perturbed negatives for
all eligible samples, run them through the ReconstructionEngine, and
save artifacts parallel to the E1-E6 negatives.

Output structure (parallel to ``neg_01``, ``neg_02``, ...):
    task5_negative_perturbation/perturbations/<sid>/ex1/
        <sid>_perturbed.json
        perturbation_meta.json
        generated.step
        kqp_result.json
        execution_report.json
        kqp_validation.json (reconstruction-engine KQP)
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "task5_negative_perturbation" / "perturbation"))

from operators_ex import op_EX1_sketch_plane_swap, op_EX2_coordinate_flip

PERT_ROOT = ROOT / "task5_negative_perturbation" / "perturbations"
EX_SUMMARY = ROOT / "task5_negative_perturbation" / "reports" / "ex_perturbation_summary.json"
REPORT_OUT = ROOT / "task5_negative_perturbation" / "reports" / "ex_negatives_generation_report.json"

CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"


def perturb_and_save(operator_name: str, op_fn, sid: str,
                       bbox: list[float], out_dir: Path) -> dict:
    """Run operator, save perturbed history + meta + reconstructed STEP."""
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_hist = json.load(open(ROOT / "Reconstruction_results" / sid
                                   / "input_history.json", encoding="utf-8"))
    dp_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
    dp = json.load(open(dp_path, encoding="utf-8")) if dp_path.exists() else {}

    try:
        pert_hist, pert_dp, meta = op_fn(clean_hist, dp)
    except Exception as e:
        return {"sample_id": sid, "operator": operator_name,
                "status": "perturb_failed", "error": f"{type(e).__name__}: {str(e)[:200]}"}

    # Save perturbed history + meta
    pert_hist_path = out_dir / f"{sid}_perturbed.json"
    pert_hist_path.write_text(json.dumps(pert_hist, indent=2, ensure_ascii=False),
                                encoding="utf-8")
    meta_path = out_dir / "perturbation_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                            encoding="utf-8")

    # Run reconstruction engine
    step_path = out_dir / "generated.step"
    exec_report = run_reconstruct(pert_hist_path, step_path, sid)
    kqp_result = run_kqp(step_path, sid) if exec_report.get("export_success") else {}
    return {"sample_id": sid, "operator": operator_name, "status": "ok",
              "meta": meta, "bbox_mm": bbox,
              "step_exists": step_path.exists(),
              "exec_report": exec_report,
              "kqp": kqp_result}


def run_reconstruct(perturbed_history: Path, out_step: Path, sample_id: str) -> dict:
    """Run the reconstruction engine on a perturbed history.

    Uses the function-based reconstruct_sample() directly (avoids
    the CLI's sample-id parsing quirk).
    """
    out_dir = out_step.parent
    try:
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(ROOT / "kqp" / "runner"))
        from reconstruction_engine.orchestrator import reconstruct_sample
        report = reconstruct_sample(perturbed_history, out_dir)
        # The orchestrator places the STEP at out_dir / <history-stem> / generated.step
        history_stem = perturbed_history.stem  # e.g., 100877_ac1e5a17_0001_perturbed
        produced_step = out_dir / history_stem / "generated.step"
        if produced_step.exists() and out_step.exists() is False:
            import shutil
            shutil.copy2(produced_step, out_step)
        return {
            "returncode": 0,
            "compile_success": report.get("compile_success"),
            "execute_success": report.get("execute_success"),
            "export_success": report.get("export_success"),
            "occt_load_success": report.get("occt_load_success"),
            "errors": report.get("errors", []),
            "export_success_at_out_step": out_step.exists() and out_step.stat().st_size > 0,
        }
    except Exception as e:
        return {"returncode": -1, "error": f"{type(e).__name__}: {str(e)[:200]}"}


def run_kqp(step_path: Path, sample_id: str) -> dict:
    """Run KQP on a STEP and return results."""
    if not step_path.exists():
        return {"error": "step not found"}
    kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sample_id}.kqp_instance.json"
    out_path = step_path.parent / "kqp_result.json"
    if not kqp_inst.exists():
        return {"error": "kqp_instance not found"}
    try:
        proc = subprocess.run(
            [CADQUERY_PYTHON,
              str(ROOT / "kqp" / "runner" / "run_kqp.py"),
              str(step_path), str(kqp_inst),
              "-o", str(out_path)],
            capture_output=True, text=True, timeout=120,
            cwd=str(ROOT))
        if out_path.exists():
            try:
                return json.loads(out_path.read_text(encoding="utf-8"))
            except Exception as e:
                return {"error": f"parse: {e}", "raw": out_path.read_text()[:200]}
        return {"returncode": proc.returncode, "stderr_tail": proc.stderr[-200:]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def main(limit_per_op: int | None = None):
    summary = json.loads(EX_SUMMARY.read_text(encoding="utf-8"))
    results = {"ex1": [], "ex2": []}

    for ex in ("EX1", "EX2"):
        op_name = "EX1_sketch_plane_swap" if ex == "EX1" else "EX2_coordinate_flip"
        op_fn = op_EX1_sketch_plane_swap if ex == "EX1" else op_EX2_coordinate_flip
        eligible = summary["eligible"][ex]
        if limit_per_op:
            eligible = eligible[:limit_per_op]

        for entry in eligible:
            sid = entry["sample_id"]
            bbox = entry.get("bbox_mm", [None, None, None])
            out_dir = PERT_ROOT / sid / ex.lower()
            print(f"[{ex}] {sid} → {out_dir.relative_to(ROOT)}")
            res = perturb_and_save(op_name, op_fn, sid, bbox, out_dir)
            results[ex.lower()].append(res)
            if res.get("status") != "ok":
                print(f"  FAIL: {res.get('error')}")
            else:
                kqp_overall = res.get("kqp", {}).get("overall_status", "?")
                print(f"  ok step_exists={res['step_exists']} kqp={kqp_overall}")

    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str),
                              encoding="utf-8")
    print(f"\nwrote {REPORT_OUT}")

    # Print summary
    for ex in ("EX1", "EX2"):
        n = len(results[ex.lower()])
        n_ok = sum(1 for r in results[ex.lower()] if r.get("status") == "ok")
        n_step = sum(1 for r in results[ex.lower()] if r.get("step_exists"))
        n_kqp_fail = sum(1 for r in results[ex.lower()]
                            if (r.get("kqp", {}).get("overall_status") == "fail"))
        n_kqp_pass = sum(1 for r in results[ex.lower()]
                            if (r.get("kqp", {}).get("overall_status") == "pass"))
        print(f"\n{ex}: total={n} ok={n_ok} step_exists={n_step} kqp_pass={n_kqp_pass} kqp_fail={n_kqp_fail}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-per-op", type=int, default=None,
                       help="cap how many EX1/EX2 negatives per operator (for smoke test)")
    args = ap.parse_args()
    main(limit_per_op=args.limit_per_op)
