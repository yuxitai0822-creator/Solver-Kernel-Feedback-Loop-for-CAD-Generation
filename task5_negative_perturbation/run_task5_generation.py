"""run_task5_generation.py — Generate 138 negative CAD candidates (3 per clean sample).

Pipeline per sample:
  1. Load clean sample's history JSON + original KQP + design_plan
  2. Run sampler.sample_perturbations_for() to get 3 specs
  3. For each spec: apply perturbation, reconstruct, save outputs to
     task5_negative_perturbation/perturbations/<sid>/<neg_id>/

Output directories
------------------
  task5_negative_perturbation/
    inputs/clean_reconstruction_set.json        (copy of frozen clean set)
    perturbations/<sample_id>/<neg_id>/
        perturbed_history.json
        perturbed_design_plan.json
        perturbation_meta.json
        reconstruction_report.json
    reports/negative_generation_summary.json
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "task5_negative_perturbation" / "perturbation"))

from perturbation.operators import detect_extent_type
from perturbation.perturb_history import apply_perturbation, run_reconstruct_engine, save_perturbed_artifacts
from perturbation.sampler import sample_perturbations_for, resolve_expected_queries


CLEAN_SET_PATH = ROOT / "Reconstruction_results" / "clean_reconstruction_set.json"
HISTORY_DIR_PRIMARY = ROOT / "data" / "sanity_set_50"
HISTORY_DIR_FALLBACK = ROOT / "Reconstruction_results"
KQP_DIR = ROOT / "kqp" / "outputs" / "compiler_v0.1"
DESIGN_PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"

OUT_ROOT = ROOT / "task5_negative_perturbation"
INPUTS_DIR = OUT_ROOT / "inputs"
PERT_DIR = OUT_ROOT / "perturbations"
REPORTS_DIR = OUT_ROOT / "reports"


def locate_history(sample_id: str) -> Path:
    """Primary source: data/sanity_set_50/<sid>.json.
    Fallback: Reconstruction_results/<sid>/input_history.json."""
    p1 = HISTORY_DIR_PRIMARY / f"{sample_id}.json"
    if p1.exists():
        return p1
    p2 = HISTORY_DIR_FALLBACK / sample_id / "input_history.json"
    if p2.exists():
        return p2
    raise FileNotFoundError(f"No history for {sample_id}")


def get_original_step(sample_id: str) -> Path:
    return HISTORY_DIR_FALLBACK / sample_id / "generated.step"


def process_one_sample(sample_id: str, symmetric_seen_flag: list[bool]) -> list[dict]:
    """Generate 3 perturbations for one sample. Returns list of report rows."""
    history_path = locate_history(sample_id)
    history = json.loads(history_path.read_text(encoding="utf-8"))
    kqp_path = KQP_DIR / f"{sample_id}.kqp_instance.json"
    dp_path = DESIGN_PLAN_DIR / f"{sample_id}.design_plan.json"
    if not kqp_path.exists():
        return []
    kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
    if dp_path.exists():
        design_plan = json.loads(dp_path.read_text(encoding="utf-8"))
    else:
        design_plan = {"solid_bodies": [{}]}

    extent = detect_extent_type(history)
    is_sym = (extent == "symmetric")

    specs = sample_perturbations_for(history,
                                       is_symmetric_sample=is_sym,
                                       symmetric_seen=symmetric_seen_flag)
    if is_sym:
        symmetric_seen_flag.append(True)

    original_step = get_original_step(sample_id)

    rows: list[dict] = []
    for spec in specs:
        neg_id = f"neg_{spec['perturbation_id']:02d}"
        out_dir = PERT_DIR / sample_id / neg_id
        out_step = out_dir / "_step_tmp.step"

        # Apply perturbation
        try:
            perturbed_h, perturbed_dp, meta = apply_perturbation(
                history, design_plan, spec)
        except Exception as e:
            # Could not apply: mark as failure
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "perturbation_meta.json").write_text(
                json.dumps({"perturbation_id": spec["perturbation_id"],
                              "operator": spec["operator"],
                              "error": f"perturbation_apply_failed: {e}",
                              "target_intent": spec["target_intent"],
                              "error_category": spec["error_category"]},
                             indent=2, ensure_ascii=False),
                encoding="utf-8")
            (out_dir / "reconstruction_report.json").write_text(
                json.dumps({"compile_success": False,
                              "execute_success": False,
                              "export_success": False,
                              "occt_load_success": False,
                              "errors": [str(e)]},
                             indent=2, ensure_ascii=False),
                encoding="utf-8")
            rows.append({
                "sample_id": sample_id,
                "negative_id": neg_id,
                "operator": spec["operator"],
                "error_category": spec["error_category"],
                "target_intent": spec["target_intent"],
                "perturbation_apply_success": False,
                "reconstruction_success": False,
                "occt_load_success": False,
                "step_size_bytes": 0,
            })
            continue

        # Resolve expected query ids
        expected_query_ids = resolve_expected_queries(spec, kqp)
        meta["expected_query_ids_resolved"] = expected_query_ids
        meta["sample_id"] = sample_id
        meta["negative_id"] = neg_id

        # Reconstruct
        try:
            rec_report = run_reconstruct_engine(perturbed_h, out_step,
                                                  perturbed_dp, sample_id)
        except Exception as e:
            rec_report = {
                "compile_success": False, "execute_success": False,
                "export_success": False, "occt_load_success": False,
                "errors": [f"reconstruct_exception: {e}"],
            }

        # Save artifacts
        save_perturbed_artifacts(
            out_dir, perturbed_h, perturbed_dp,
            meta, rec_report,
            perturbed_step_path=out_step if rec_report.get("export_success") else None,
            original_step_path=original_step,
        )
        # Cleanup temp step
        try:
            if out_step.exists():
                out_step.unlink()
        except OSError:
            pass

        rows.append({
            "sample_id": sample_id,
            "negative_id": neg_id,
            "operator": spec["operator"],
            "error_category": spec["error_category"],
            "target_intent": spec["target_intent"],
            "expected_query_ids": expected_query_ids,
            "perturbation_apply_success": True,
            "reconstruction_success": (rec_report.get("compile_success")
                                          and rec_report.get("execute_success")
                                          and rec_report.get("export_success")
                                          and rec_report.get("occt_load_success")),
            "occt_load_success": rec_report.get("occt_load_success"),
            "step_size_bytes": (out_dir / "generated.step").stat().st_size
                                if (out_dir / "generated.step").exists() else 0,
        })
    return rows


def main():
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    PERT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Always refresh the inputs snapshot
    shutil.copy2(CLEAN_SET_PATH, INPUTS_DIR / "clean_reconstruction_set.json")

    clean_set = json.loads(CLEAN_SET_PATH.read_text(encoding="utf-8"))
    clean_samples = clean_set["clean_samples"]

    all_rows: list[dict] = []
    sym_flag: list[bool] = []
    t0 = time.time()
    for i, s in enumerate(clean_samples):
        sid = s["sample_id"]
        rows = process_one_sample(sid, sym_flag)
        all_rows.extend(rows)
        rate = sum(1 for r in all_rows if r.get("reconstruction_success")) / max(1, len(all_rows))
        print(f"[{i+1:3d}/{len(clean_samples)}] {sid}: "
              f"applied={sum(1 for r in rows if r.get('perturbation_apply_success'))}/{len(rows)}, "
              f"rec_ok={sum(1 for r in rows if r.get('reconstruction_success'))}/{len(rows)}, "
              f"running_rate={rate:.2%}, "
              f"elapsed={time.time()-t0:.0f}s")

    # Summary
    summary = {
        "total_samples": len(clean_samples),
        "total_negatives": len(all_rows),
        "target_negatives": 138,
        "perturbations_per_sample": 3,
        "perturbation_apply_success_count": sum(1 for r in all_rows
                                                  if r.get("perturbation_apply_success")),
        "reconstruction_success_count": sum(1 for r in all_rows
                                              if r.get("reconstruction_success")),
        "operator_distribution": {},
        "error_category_distribution": {},
        "target_intent_distribution": {},
        "per_negative_rows": all_rows,
    }
    for r in all_rows:
        op = r.get("operator")
        ec = r.get("error_category")
        ti = r.get("target_intent")
        summary["operator_distribution"].setdefault(op, 0)
        summary["operator_distribution"][op] += 1
        summary["error_category_distribution"].setdefault(ec, 0)
        summary["error_category_distribution"][ec] += 1
        summary["target_intent_distribution"].setdefault(ti, 0)
        summary["target_intent_distribution"][ti] += 1

    summary["reconstruction_rate"] = (
        summary["reconstruction_success_count"]
        / max(1, summary["perturbation_apply_success_count"]))

    (REPORTS_DIR / "negative_generation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print("\n=== Task5 Generation Summary ===")
    print(f"Total negatives: {summary['total_negatives']} / target {summary['target_negatives']}")
    print(f"Perturbation apply success: {summary['perturbation_apply_success_count']}")
    print(f"Reconstruction success: {summary['reconstruction_success_count']} "
          f"({summary['reconstruction_rate']:.2%})")
    print(f"Operator distribution: {json.dumps(summary['operator_distribution'], indent=2)}")
    print(f"Target intent distribution: {json.dumps(summary['target_intent_distribution'], indent=2)}")


if __name__ == "__main__":
    main()
