"""run_task5_kqp_detection.py — Run frozen KQP runner on every negative STEP.

For each perturbation:
  1. Load perturbed_history + reconstruction_report from
     task5_negative_perturbation/perturbations/<sid>/<neg_id>/
  2. Skip negatives where reconstruction failed
  3. Skip negatives where kqp_result.json already present (resumable)
  4. Run kqp.runner.run_kqp.run_kqp() with the FROZEN original KQP instance
  5. Save to neg_dir/kqp_result.json
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))


PERT_DIR = ROOT / "task5_negative_perturbation" / "perturbations"
KQP_DIR = ROOT / "kqp" / "outputs" / "compiler_v0.1"
DESIGN_PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"
REPORTS_DIR = ROOT / "task5_negative_perturbation" / "reports"


def run_kqp_subprocess(step_path: Path, kqp_path: Path,
                          dp_path: Path, out_path: Path) -> int:
    """Call kqp runner as a subprocess (OCCT can segfault in-process)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    runner = ROOT / "kqp" / "runner" / "run_kqp.py"
    cmd = [sys.executable, str(runner), str(step_path), str(kqp_path)]
    if dp_path.exists():
        cmd.extend(["--design-plan", str(dp_path)])
    cmd.extend(["-o", str(out_path)])
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return p.returncode


def main():
    if not PERT_DIR.exists():
        print(f"No perturbations dir: {PERT_DIR}")
        return
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    n_dirs = sum(1 for _ in PERT_DIR.glob("*/*"))
    t0 = time.time()
    i = 0
    for sample_dir in sorted(PERT_DIR.iterdir()):
        if not sample_dir.is_dir():
            continue
        sid = sample_dir.name
        for neg_dir in sorted(sample_dir.iterdir()):
            if not neg_dir.is_dir():
                continue
            neg_id = neg_dir.name
            i += 1
            step_path = neg_dir / "generated.step"
            kqp_path = KQP_DIR / f"{sid}.kqp_instance.json"
            dp_path = DESIGN_PLAN_DIR / f"{sid}.design_plan.json"
            out_path = neg_dir / "kqp_result.json"

            if not step_path.exists():
                rows.append({"sample_id": sid, "negative_id": neg_id,
                                "step_exists": False, "kqp_run": "skipped"})
                continue

            if out_path.exists():
                rows.append({"sample_id": sid, "negative_id": neg_id,
                                "step_exists": True,
                                "kqp_run": "cached",
                                "cached_path": str(out_path)})
                continue

            try:
                rc = run_kqp_subprocess(step_path, kqp_path, dp_path, out_path)
                rows.append({"sample_id": sid, "negative_id": neg_id,
                                "step_exists": True,
                                "kqp_run": "ran",
                                "returncode": rc,
                                "result_path": str(out_path)})
            except subprocess.TimeoutExpired:
                rows.append({"sample_id": sid, "negative_id": neg_id,
                                "step_exists": True,
                                "kqp_run": "timeout"})
            except Exception as e:
                rows.append({"sample_id": sid, "negative_id": neg_id,
                                "step_exists": True,
                                "kqp_run": "exception",
                                "error": str(e)})

            if i % 20 == 0:
                print(f"  [{i}/{n_dirs}] last={sid}/{neg_id} rc={rc} "
                      f"elapsed={time.time()-t0:.0f}s")

    summary = {
        "total_negatives_attempted": len(rows),
        "ran": sum(1 for r in rows if r["kqp_run"] == "ran"),
        "cached": sum(1 for r in rows if r["kqp_run"] == "cached"),
        "skipped_no_step": sum(1 for r in rows if r["kqp_run"] == "skipped"),
        "timeout": sum(1 for r in rows if r["kqp_run"] == "timeout"),
        "exception": sum(1 for r in rows if r["kqp_run"] == "exception"),
        "rows": rows,
    }
    (REPORTS_DIR / "kqp_run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"\nKQP run complete. ran={summary['ran']} cached={summary['cached']} "
          f"timeout={summary['timeout']} exception={summary['exception']}")


if __name__ == "__main__":
    main()
