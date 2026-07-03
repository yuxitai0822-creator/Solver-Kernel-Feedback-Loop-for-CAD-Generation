"""orchestrator.py — End-to-end pipeline: history JSON → generated code → STEP → OCCT load.

For each sample:
  1. compile_history → generated code + compile_report
  2. execute_generated_code → step file + exec_report
  3. load_step (via KQP runner's step_loader) → occt_load_report
  4. Write all per-sample outputs (code, step, stdout, stderr, reports) under
     Reconstruction_results/<sample_id>/

Phase 1 verification metrics (level 0):
  compile_success: True
  execute_success: True
  export_success: True
  occt_load_success: True
  unsupported_ops: [] (list of unsupported op descriptions)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any

# Ensure the parent dir is on path so we can import from sibling packages
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kqp" / "runner"))
sys.path.insert(0, str(ROOT))

from reconstruction_engine.compiler import compile_history
from reconstruction_engine.executor import execute_generated_code
from kqp.runner.step_loader import load_step


def reconstruct_sample(history_path: str | Path, results_dir: str | Path) -> dict:
    """Run the full reconstruction pipeline on one sample.

    Returns the execution report dict.
    """
    history_path = Path(history_path)
    sample_id = history_path.stem
    sample_dir = Path(results_dir) / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    # 1. Compile
    code, compile_report = compile_history(history_path)
    (sample_dir / "input_history.json").write_text(history_path.read_text(encoding="utf-8"))
    (sample_dir / "generated_code.py").write_text(code, encoding="utf-8")

    # 2. Execute
    step_path = sample_dir / "generated.step"
    exec_report = execute_generated_code(code, step_path, history_path)
    (sample_dir / "stdout.txt").write_text(exec_report["stdout"], encoding="utf-8")
    (sample_dir / "stderr.txt").write_text(exec_report["stderr"], encoding="utf-8")

    # 3. OCCT load (only if STEP was exported)
    if exec_report["export_success"]:
        try:
            shape, status = load_step(step_path)
            occt_load_success = (shape is not None and not shape.IsNull())
        except Exception as e:
            occt_load_success = False
            status = f"load error: {e}"
    else:
        occt_load_success = False
        status = "skipped (export failed)"

    # 4. Write execution_report.json
    report = {
        "sample_id": sample_id,
        "compile_success": compile_report["compile_success"],
        "execute_success": exec_report["execute_success"],
        "export_success": exec_report["export_success"],
        "occt_load_success": occt_load_success,
        "occt_load_status": status,
        "unsupported_ops": compile_report.get("unsupported_ops", []),
        "errors": [e for e in (compile_report.get("compile_error"),
                              exec_report.get("error")) if e],
        "extent_type": compile_report.get("extent_type"),
        "sketch_curve_count": compile_report.get("sketch_curve_count"),
        "consumed_profile_count": compile_report.get("consumed_profile_count"),
    }
    (sample_dir / "execution_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def reconstruct_batch(manifest_path: str | Path, results_dir: str | Path,
                        sample_ids: list[str] | None = None) -> dict:
    """Run reconstruction on all 50 samples (or a subset).

    Returns aggregate report.
    """
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    import json as _j
    manifest = _j.load(open(manifest_path, encoding="utf-8"))
    all_ids = [e["id"] for e in manifest["entries"]]

    if sample_ids is None:
        sample_ids = all_ids

    history_dir = ROOT / "data" / "sanity_set_50"
    per_sample = []
    for sid in sample_ids:
        hp = history_dir / f"{sid}.json"
        if not hp.exists():
            per_sample.append({"sample_id": sid, "compile_success": False,
                                "execute_success": False, "export_success": False,
                                "occt_load_success": False, "error": "history not found"})
            continue
        r = reconstruct_sample(hp, results_dir)
        r["sample_id"] = sid
        per_sample.append(r)
        # Progress
        s = "+" if r["compile_success"] and r["execute_success"] and r["export_success"] and r["occt_load_success"] else "!"
        print(f"  {s} {sid}: c={r['compile_success']} e={r['execute_success']} x={r['export_success']} l={r['occt_load_success']}")

    # Aggregate
    n = len(per_sample)
    n_c = sum(1 for r in per_sample if r["compile_success"])
    n_e = sum(1 for r in per_sample if r["execute_success"])
    n_x = sum(1 for r in per_sample if r["export_success"])
    n_l = sum(1 for r in per_sample if r["occt_load_success"])
    n_full = sum(1 for r in per_sample
                  if r["compile_success"] and r["execute_success"]
                  and r["export_success"] and r["occt_load_success"])
    all_unsupported = []
    for r in per_sample:
        all_unsupported.extend(r.get("unsupported_ops", []))

    summary = {
        "total_samples": n,
        "compile_success": n_c,
        "execute_success": n_e,
        "export_success": n_x,
        "occt_load_success": n_l,
        "full_pipeline_success": n_full,
        "unsupported_ops_count": len(all_unsupported),
        "unique_unsupported_ops": sorted(set(all_unsupported)),
        "errors": [{"sample_id": r["sample_id"], "error": r.get("error")}
                   for r in per_sample if r.get("error")],
        "per_sample": per_sample,
    }
    (results_dir / "_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
