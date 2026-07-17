"""run_missing_and_revalidate.py — Incremental recovery from the previous batch.

Two-phase recovery that avoids redoing the entire 132-negative batch:

  Phase A: re-run ONLY the negatives missing from disk (38 in the last run).
  Phase B: re-validate delta/alignment for ALL existing negatives using the
           V0.1.4 validators (which now handle sketch_polygon).

After both phases, regenerate ``compile_summary.json`` and the
``repair_eligible_manifest.json`` from the union of new + old results.

Usage:
    python experiments/history2ir/batch/run_missing_and_revalidate.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve()
# Walk up until we find the project root (contains Reconstruction_results/)
while ROOT.parent != ROOT and not (ROOT / "Reconstruction_results").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "history2ir"))
sys.path.insert(0, str(ROOT))

from history2ir.batch.run_history2ir import (
    compile_and_save, run_adaptor_subprocess, run_kqp_subprocess,
    compile_negative_set, compile_clean_set,
)
from history2ir.validation.validators import (
    validate_delta_consistency, compute_perturbation_alignment_report,
    compare_kqp_equivalence,
)

CLEAN_HIST_DIR = ROOT / "Reconstruction_results"
NEG_PERT_ROOT = ROOT / "task5_negative_perturbation" / "perturbations"
TASK5_ADAPTOR_SUMMARY = (ROOT / "task5_negative_perturbation"
                              / "reports" / "adaptor_run_summary.json")
TASK5_KQP_SUMMARY = (ROOT / "task5_negative_perturbation"
                        / "reports" / "kqp_detection_summary.json")
CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"

OUT_ROOT = ROOT / "experiments" / "history2ir" / "results"
REPORTS = ROOT / "experiments" / "history2ir" / "reports"


def phase_a_run_missing():
    """Run only negatives not yet on disk."""
    adapt_summary = None
    if TASK5_ADAPTOR_SUMMARY.exists():
        adapt_summary = json.loads(
            TASK5_ADAPTOR_SUMMARY.read_text(encoding="utf-8"))
    elif TASK5_KQP_SUMMARY.exists():
        kqp = json.loads(TASK5_KQP_SUMMARY.read_text(encoding="utf-8"))
        adapt_summary = {
            "rows": [
                {"sample_id": r["sample_id"],
                 "negative_id": r.get("negative_id", "neg_01"),
                 "reconstruction_success": r.get(
                     "eligible_for_detection_eval", False)}
                for r in kqp.get("rows", [])
            ]
        }
    valid_neg = [r for r in (adapt_summary or {}).get("rows", [])
                   if r.get("reconstruction_success")]

    missing = []
    for neg in valid_neg:
        sid = neg["sample_id"]
        nid = neg.get("negative_id") or "neg_01"
        out_dir = OUT_ROOT / "negative" / sid / nid
        if not (out_dir / "compile_report.json").exists():
            missing.append(neg)

    print(f"[Phase A] missing negatives on disk: {len(missing)}")
    if not missing:
        return []

    slim = {"rows": missing}
    rows = compile_negative_set(slim)
    return rows


def phase_b_revalidate_all():
    """Re-validate delta + alignment for every negative directory on disk,
    using the new V0.1.4 validators."""
    print("[Phase B] re-validating delta + alignment for all existing negatives")
    out_rows = []
    n_revalidated = 0
    for sid in sorted(os.listdir(OUT_ROOT / "negative")):
        for nid in sorted(os.listdir(OUT_ROOT / "negative" / sid)):
            if not nid.startswith("neg_"):
                continue
            out_dir = OUT_ROOT / "negative" / sid / nid
            cad_ir_path = out_dir / "cad_ir.json"
            clean_ir_path = OUT_ROOT / "clean" / sid / "cad_ir.json"
            pert_meta_path = (NEG_PERT_ROOT / sid / nid
                                / "perturbation_meta.json")
            if not (cad_ir_path.exists() and clean_ir_path.exists()
                    and pert_meta_path.exists()):
                continue
            with open(cad_ir_path, encoding="utf-8") as f:
                ir_neg = json.load(f)
            with open(clean_ir_path, encoding="utf-8") as f:
                ir_clean = json.load(f)
            with open(pert_meta_path, encoding="utf-8") as f:
                meta = json.load(f)

            delta = validate_delta_consistency(ir_clean, ir_neg, meta)
            align = compute_perturbation_alignment_report(ir_clean, ir_neg, meta)

            (out_dir / "delta_consistency_report.json").write_text(
                json.dumps({
                    "sample_id": sid, "negative_id": nid,
                    "perturbation_type": meta.get("operator_input_name"),
                    "validation": delta,
                }, indent=2, ensure_ascii=False),
                encoding="utf-8")
            (out_dir / "perturbation_alignment_report.json").write_text(
                json.dumps(align, indent=2, ensure_ascii=False),
                encoding="utf-8")
            n_revalidated += 1
    print(f"[Phase B] revalidated {n_revalidated} negatives")


def phase_c_recompute_behavioral_equivalence():
    """Re-run compare_kqp_equivalence for all existing negatives using the
    V0.1.4 code path (no logic change but centralises access)."""
    print("[Phase C] recomputing behavioral_equivalence for all negatives")
    n = 0
    for sid in sorted(os.listdir(OUT_ROOT / "negative")):
        for nid in sorted(os.listdir(OUT_ROOT / "negative" / sid)):
            if not nid.startswith("neg_"):
                continue
            out_dir = OUT_ROOT / "negative" / sid / nid
            kqp_hist_path = NEG_PERT_ROOT / sid / nid / "kqp_result.json"
            kqp_ir_path = out_dir / "kqp_result.json"
            if not (kqp_hist_path.exists() and kqp_ir_path.exists()):
                continue
            try:
                with open(kqp_hist_path, encoding="utf-8") as f:
                    kqp_hist = json.load(f)
                with open(kqp_ir_path, encoding="utf-8") as f:
                    kqp_ir = json.load(f)
                beq = compare_kqp_equivalence(kqp_hist, kqp_ir)
                (out_dir / "behavioral_equivalence_report.json").write_text(
                    json.dumps(beq, indent=2, ensure_ascii=False),
                    encoding="utf-8")
                n += 1
            except Exception as e:
                print(f"  BEQ error on {sid}/{nid}: {e}")
    print(f"[Phase C] recomputed {n} behavioral_equivalence reports")


def phase_d_aggregate():
    """Read all results + manifests → build compile_summary.json + manifest."""
    print("[Phase D] aggregating compile_summary.json + repair_eligible_manifest.json")
    clean_set_path = CLEAN_HIST_DIR / "clean_reconstruction_set.json"
    clean_set = json.loads(clean_set_path.read_text(encoding="utf-8"))

    clean_rows = []
    for s in clean_set["clean_samples"]:
        sid = s["sample_id"]
        out_dir = OUT_ROOT / "clean" / sid
        cr_path = out_dir / "compile_report.json"
        er_path = out_dir / "execution_report.json"
        if cr_path.exists():
            with open(cr_path, encoding="utf-8") as f:
                cr = json.load(f)
            adapt_status = None
            kqp_status = None
            if er_path.exists():
                with open(er_path, encoding="utf-8") as f:
                    er = json.load(f)
                adapt_status = er.get("adaptor_status")
                kqp_status = er.get("kqp_overall_status")
            clean_rows.append({
                "sample_id": sid, "label": "clean",
                "ir_path": str(out_dir.relative_to(ROOT)),
                "compile_pass": cr.get("overall") == "pass",
                "adaptor_status": adapt_status,
                "kqp_status": kqp_status,
            })

    neg_rows = []
    for sid in sorted(os.listdir(OUT_ROOT / "negative")):
        for nid in sorted(os.listdir(OUT_ROOT / "negative" / sid)):
            if not nid.startswith("neg_"):
                continue
            out_dir = OUT_ROOT / "negative" / sid / nid
            cr_path = out_dir / "compile_report.json"
            er_path = out_dir / "execution_report.json"
            d_path = out_dir / "delta_consistency_report.json"
            a_path = out_dir / "perturbation_alignment_report.json"
            b_path = out_dir / "behavioral_equivalence_report.json"
            kqp_h_path = NEG_PERT_ROOT / sid / nid / "kqp_result.json"
            if not cr_path.exists():
                continue
            with open(cr_path, encoding="utf-8") as f:
                cr = json.load(f)
            er = {}
            if er_path.exists():
                with open(er_path, encoding="utf-8") as f:
                    er = json.load(f)
            beq = {}
            if b_path.exists():
                with open(b_path, encoding="utf-8") as f:
                    beq = json.load(f)
            delta = {"validation": {"passed": False}}
            if d_path.exists():
                with open(d_path, encoding="utf-8") as f:
                    delta = json.load(f)
            align = {"delta_consistent": False}
            if a_path.exists():
                with open(a_path, encoding="utf-8") as f:
                    align = json.load(f)
            kqp_history = {}
            if kqp_h_path.exists():
                with open(kqp_h_path, encoding="utf-8") as f:
                    kqp_history = json.load(f)

            compile_pass = cr.get("overall") == "pass"
            step_exists = bool(er.get("step_exists"))
            sample_agree = beq.get("sample_level_agreement", False)
            targeted = beq.get("targeted_failure_preserved", False)
            delta_ok = delta.get("validation", {}).get("passed", False)
            align_ok = align.get("delta_consistent", False)
            repair_eligible = (compile_pass and er.get("adaptor_status") == "success"
                                 and step_exists and sample_agree and targeted)

            neg_rows.append({
                "sample_id": sid, "negative_id": nid, "label": "negative",
                "compile_pass": compile_pass,
                "adaptor_status": er.get("adaptor_status"),
                "step_exists": step_exists,
                "kqp_history_status": kqp_history.get("overall_status"),
                "kqp_ir_status": (json.loads(
                    (out_dir / "kqp_result.json").read_text(encoding="utf-8")
                ).get("overall_status") if (out_dir / "kqp_result.json").exists() else None),
                "sample_agree": sample_agree,
                "targeted_failure_preserved": targeted,
                "delta_consistent": delta_ok,
                "perturbation_aligned": align_ok,
                "repair_eligible": repair_eligible,
            })

    n_clean = len(clean_rows)
    n_clean_pass = sum(1 for r in clean_rows if r.get("compile_pass"))
    n_neg = len(neg_rows)
    n_neg_pass = sum(1 for r in neg_rows if r.get("compile_pass"))
    n_repair = sum(1 for r in neg_rows if r.get("repair_eligible"))

    summary = {
        "phase": "Task 2 — History2IR Compiler v0.1.4",
        "n_clean": n_clean, "n_clean_compile_pass": n_clean_pass,
        "n_negative": n_neg, "n_negative_compile_pass": n_neg_pass,
        "n_repair_eligible": n_repair,
        "clean_rows": clean_rows,
        "negative_rows": neg_rows,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "compile_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")

    eligible = [r for r in neg_rows if r.get("repair_eligible")]
    manifest = {
        "phase": "Repair Eligible Negative Set v0.1.4",
        "criteria": "compile_pass AND adaptor success AND step_exists "
                      "AND behavioral_equivalence.sample_agree "
                      "AND behavioral_equivalence.targeted_failure_preserved",
        "n_eligible": len(eligible),
        "n_total_negatives": n_neg,
        "eligible_ratio": len(eligible) / max(1, n_neg),
        "samples": [{"sample_id": r["sample_id"],
                       "negative_id": r["negative_id"]} for r in eligible],
    }
    (REPORTS / "repair_eligible_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8")

    print(f"[Phase D] clean {n_clean_pass}/{n_clean} pass, "
          f"neg {n_neg_pass}/{n_neg} compile, "
          f"{n_repair}/{n_neg} repair-eligible "
          f"({100*n_repair/max(1,n_neg):.1f}%)")
    return summary


def main():
    t0 = time.time()
    phase_a_run_missing()
    print(f"  Phase A took {time.time()-t0:.1f}s")
    t1 = time.time()
    phase_b_revalidate_all()
    print(f"  Phase B took {time.time()-t1:.1f}s")
    t2 = time.time()
    phase_c_recompute_behavioral_equivalence()
    print(f"  Phase C took {time.time()-t2:.1f}s")
    t3 = time.time()
    summary = phase_d_aggregate()
    print(f"  Phase D took {time.time()-t3:.1f}s")
    print(f"Total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()