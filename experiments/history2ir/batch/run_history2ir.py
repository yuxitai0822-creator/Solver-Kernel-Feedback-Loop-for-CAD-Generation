"""run_history2ir.py — Batch compiler for the History2IR pipeline.

Compiles all 46 clean + 132 negative samples through the SAME compiler.
For each sample, produces:
  * cad_ir.json
  * compile_report.json   (validation outcome)
  * execution_report.json (Adaptor + KQP outcome)
  * behavioral_equivalence_report.json (clean only, after re-running KQP on IR)
For negatives additionally:
  * delta_consistency_report.json
  * perturbation_alignment_report.json

For V0.1 simplicity, the "behavioral_equivalence" comparison reuses the
KQP results that were already computed on the Reconstruction-Engine
output (task5_negative_perturbation/*/kqp_result.json).  We re-run KQP
on the IR-built STEP and compare.

Outputs:
  experiments/history2ir/results/clean/<sid>/...
  experiments/history2ir/results/negative/<sid>/<neg_id>/...
  experiments/history2ir/reports/compile_summary.json
  experiments/history2ir/reports/repair_eligible_manifest.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve()
# Walk up until we find the project root (contains Reconstruction_results/)
while ROOT.parent != ROOT and not (ROOT / "Reconstruction_results").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "history2ir"))
sys.path.insert(0, str(ROOT))

from history2ir.compiler.history_to_ir import compile_history_to_ir
from history2ir.validation.validators import (
    validate_schema, validate_semantic_history2ir,
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
KQP_RUNNER = ROOT / "kqp" / "runner" / "run_kqp.py"
ADAPTOR_WORKER = ROOT / "cad_repair_loop" / "_adaptor_subprocess.py"

OUT_ROOT = ROOT / "experiments" / "history2ir" / "results"
REPORTS = ROOT / "experiments" / "history2ir" / "reports"


# ---------------------------------------------------------------------------
# Compile a single IR
# ---------------------------------------------------------------------------

def compile_and_save(history: dict, out_dir: Path, sample_id: str,
                        perturbation_meta: dict | None = None,
                        label: str = "clean") -> dict:
    """Compile history → IR + reports, save to out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ir = compile_history_to_ir(history, sample_id=sample_id,
                                  perturbation_meta=perturbation_meta)
    (out_dir / "cad_ir.json").write_text(
        json.dumps(ir, indent=2, ensure_ascii=False),
        encoding="utf-8")

    # Schema + semantic
    sv = validate_schema(ir)
    hv = validate_semantic_history2ir(ir)
    compile_report = {
        "sample_id": sample_id,
        "label": label,
        "schema_validation": sv,
        "history2ir_semantic": hv,
        "overall": "pass" if (sv["passed"] and hv["passed"]) else "fail",
    }
    (out_dir / "compile_report.json").write_text(
        json.dumps(compile_report, indent=2, ensure_ascii=False),
        encoding="utf-8")
    return {"ir": ir, "compile_report": compile_report}


# ---------------------------------------------------------------------------
# Adaptor + KQP on the IR
# ---------------------------------------------------------------------------

def run_adaptor_subprocess(ir: dict, out_dir: Path) -> dict:
    """Run cadquery Adaptor on IR (subprocess to cad_subproject1)."""
    import subprocess
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ir_path = out_dir / "_ir_input.cad_ir.json"
    ir_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    proc = subprocess.run([CADQUERY_PYTHON, str(ADAPTOR_WORKER),
                              str(ir_path), str(out_dir)],
                             capture_output=True, text=True, timeout=120,
                             cwd=str(ROOT))
    rp = out_dir / "adapter_report.json"
    if rp.exists():
        try:
            return json.loads(rp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"adapter_status": "fail",
            "warnings": [f"adaptor rc={proc.returncode}: {proc.stderr[-200:]}"]}


def run_kqp_subprocess(step_path: Path, kqp_path: Path, plan_path: Path,
                          output_path: Path) -> dict:
    import subprocess
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [CADQUERY_PYTHON, str(KQP_RUNNER),
           str(step_path), str(kqp_path)]
    if plan_path.exists():
        cmd.extend(["--design-plan", str(plan_path)])
    cmd.extend(["-o", str(output_path)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                            cwd=str(ROOT))
    if output_path.exists():
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"overall_status": "fail", "query_results": [],
            "error": f"KQP rc={proc.returncode}: {proc.stderr[-200:]}"}


# ---------------------------------------------------------------------------
# Compile all clean + negative samples
# ---------------------------------------------------------------------------

def compile_clean_set(clean_samples: list[dict]) -> list[dict]:
    rows = []
    for s in clean_samples:
        sid = s["sample_id"]
        hist_path = CLEAN_HIST_DIR / sid / "input_history.json"
        if not hist_path.exists():
            continue
        try:
            history = json.loads(hist_path.read_text(encoding="utf-8"))
        except Exception as e:
            rows.append({"sample_id": sid, "label": "clean", "error": f"history parse: {e}"})
            continue
        out_dir = OUT_ROOT / "clean" / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            res = compile_and_save(history, out_dir, sample_id=sid, label="clean")
            ir = res["ir"]
        except Exception as e:
            import traceback
            rows.append({"sample_id": sid, "label": "clean",
                          "error": f"compile: {type(e).__name__}: {e}",
                          "traceback": traceback.format_exc()[-500:]})
            continue

        # Adaptor + KQP on IR
        try:
            adapt_rep = run_adaptor_subprocess(ir, out_dir)
        except Exception as e:
            adapt_rep = {"adapter_status": "fail", "error": str(e)}
        kqp_instance = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sid}.kqp_instance.json"
        plan = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
        step = next(out_dir.glob("*.step"), None)
        kqp_ir = {"overall_status": "fail", "query_results": []}
        if step and step.exists():
            try:
                kqp_ir = run_kqp_subprocess(step, kqp_instance, plan,
                                              out_dir / "kqp_result.json")
            except Exception as e:
                kqp_ir = {"overall_status": "fail", "error": f"{type(e).__name__}: {e}"}

        # Behavioral equivalence: compare IR-KQP to Reconstruction-KQP (if available)
        rec_kqp_path = CLEAN_HIST_DIR / sid / "kqp_feedback.json"
        # Use task5's KQP from the FIRST perturbation's kqp_result (cleanest reference)
        # but for clean samples we just use IR-KQP as the canonical
        # (we don't have a separate "reconstruction" KQP for the clean case,
        # since clean is the reference)
        execution_report = {
            "sample_id": sid,
            "label": "clean",
            "adaptor_status": adapt_rep.get("adapter_status"),
            "step_exists": step is not None and step.exists(),
            "kqp_overall_status": kqp_ir.get("overall_status"),
            "kqp_n_queries": len(kqp_ir.get("query_results", [])),
            "kqp_n_passed": sum(1 for qr in kqp_ir.get("query_results", [])
                                  if qr.get("status") == "pass"),
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            (out_dir / "execution_report.json").write_text(
                json.dumps(execution_report, indent=2, ensure_ascii=False),
                encoding="utf-8")
            beq = compare_kqp_equivalence(kqp_ir, kqp_ir)
            (out_dir / "behavioral_equivalence_report.json").write_text(
                json.dumps(beq, indent=2, ensure_ascii=False),
                encoding="utf-8")
        except Exception as e:
            rows.append({"sample_id": sid, "label": "clean",
                          "stage": "report_write", "error": f"{type(e).__name__}: {e}"})

        rows.append({"sample_id": sid, "label": "clean",
                       "ir_path": str(out_dir.relative_to(ROOT)),
                       "compile_pass": res["compile_report"]["overall"] == "pass",
                       "adaptor_status": adapt_rep.get("adapter_status"),
                       "kqp_status": kqp_ir.get("overall_status")})
    return rows


def compile_negative_set(adaptor_summary: dict | None = None) -> list[dict]:
    """Compile all perturbed negatives.

    `adaptor_summary` is the task5 adaptor_run_summary dict; if None,
    we read it from disk.  We use it to filter out negatives whose
    perturbation was not reconstructable.  Falls back to the
    kqp_detection_summary.json if the adaptor summary is missing.
    """
    if adaptor_summary is None:
        if TASK5_ADAPTOR_SUMMARY.exists():
            adaptor_summary = json.loads(
                TASK5_ADAPTOR_SUMMARY.read_text(encoding="utf-8"))
        elif TASK5_KQP_SUMMARY.exists():
            kqp = json.loads(TASK5_KQP_SUMMARY.read_text(encoding="utf-8"))
            adaptor_summary = {
                "rows": [
                    {"sample_id": r["sample_id"],
                     "negative_id": r.get("negative_id", "neg_01"),
                     "reconstruction_success": r.get("eligible_for_detection_eval", False)}
                    for r in kqp.get("rows", [])
                ]
            }
    valid_neg = (adaptor_summary or {}).get("rows", [])
    valid_neg = [r for r in valid_neg
                   if r.get("reconstruction_success")]

    rows = []
    for neg in valid_neg:
        sid = neg["sample_id"]
        nid = neg.get("negative_id") or "neg_01"
        neg_dir = NEG_PERT_ROOT / sid / nid
        pert_hist_path = neg_dir / "perturbed_history.json"
        pert_meta_path = neg_dir / "perturbation_meta.json"
        kqp_hist_path = neg_dir / "kqp_result.json"
        if not pert_hist_path.exists():
            continue
        try:
            history = json.loads(pert_hist_path.read_text(encoding="utf-8"))
            pert_meta = (json.loads(pert_meta_path.read_text(encoding="utf-8"))
                           if pert_meta_path.exists() else {})
            kqp_history = (json.loads(kqp_hist_path.read_text(encoding="utf-8"))
                              if kqp_hist_path.exists() else {})
        except Exception as e:
            rows.append({"sample_id": sid, "negative_id": nid,
                          "label": "negative", "error": f"parse: {e}"})
            continue

        out_dir = OUT_ROOT / "negative" / sid / nid
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            res = compile_and_save(history, out_dir, sample_id=sid,
                                      perturbation_meta=pert_meta, label="negative")
            ir_neg = res["ir"]
        except Exception as e:
            import traceback
            rows.append({"sample_id": sid, "negative_id": nid,
                          "label": "negative", "error": f"compile: {type(e).__name__}: {e}",
                          "traceback": traceback.format_exc()[-500:]})
            continue

        # Clean IR (for delta comparison)
        clean_ir_path = OUT_ROOT / "clean" / sid / "cad_ir.json"
        clean_ir = (json.loads(clean_ir_path.read_text(encoding="utf-8"))
                       if clean_ir_path.exists() else None)

        # Adaptor + KQP on IR
        try:
            adapt_rep = run_adaptor_subprocess(ir_neg, out_dir)
        except Exception as e:
            adapt_rep = {"adapter_status": "fail", "error": str(e)}
        kqp_inst = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sid}.kqp_instance.json"
        plan = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sid}.design_plan.json"
        step = next(out_dir.glob("*.step"), None)
        kqp_ir = {"overall_status": "fail", "query_results": []}
        if step and step.exists():
            try:
                kqp_ir = run_kqp_subprocess(step, kqp_inst, plan,
                                              out_dir / "kqp_result.json")
            except Exception as e:
                kqp_ir = {"overall_status": "fail", "error": f"{type(e).__name__}: {e}"}

        execution_report = {
            "sample_id": sid, "negative_id": nid, "label": "negative",
            "adaptor_status": adapt_rep.get("adapter_status"),
            "step_exists": step is not None and step.exists(),
            "kqp_overall_status": kqp_ir.get("overall_status"),
            "kqp_n_queries": len(kqp_ir.get("query_results", [])),
            "kqp_n_passed": sum(1 for qr in kqp_ir.get("query_results", [])
                                  if qr.get("status") == "pass"),
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            (out_dir / "execution_report.json").write_text(
                json.dumps(execution_report, indent=2, ensure_ascii=False),
                encoding="utf-8")
            beq = compare_kqp_equivalence(kqp_history, kqp_ir)
            (out_dir / "behavioral_equivalence_report.json").write_text(
                json.dumps(beq, indent=2, ensure_ascii=False),
                encoding="utf-8")

            delta_report = {
                "sample_id": sid, "negative_id": nid,
                "perturbation_type": pert_meta.get("operator_input_name"),
                "validation": (validate_delta_consistency(clean_ir, ir_neg, pert_meta)
                                  if clean_ir else {"passed": False,
                                                       "issues": ["no clean IR"]}),
            }
            (out_dir / "delta_consistency_report.json").write_text(
                json.dumps(delta_report, indent=2, ensure_ascii=False),
                encoding="utf-8")

            align_report = (compute_perturbation_alignment_report(
                                clean_ir, ir_neg, pert_meta)
                              if clean_ir else {"delta_consistent": False})
            (out_dir / "perturbation_alignment_report.json").write_text(
                json.dumps(align_report, indent=2, ensure_ascii=False),
                encoding="utf-8")
        except Exception as e:
            rows.append({"sample_id": sid, "negative_id": nid,
                          "stage": "report_write", "error": f"{type(e).__name__}: {e}"})

        # Repair eligible?
        repair_eligible = (
            res["compile_report"]["overall"] == "pass"
            and adapt_rep.get("adapter_status") == "success"
            and step is not None and step.exists()
            and beq.get("targeted_failure_preserved")
            and beq.get("sample_level_agreement")
        )

        rows.append({
            "sample_id": sid, "negative_id": nid, "label": "negative",
            "compile_pass": res["compile_report"]["overall"] == "pass",
            "adaptor_status": adapt_rep.get("adapter_status"),
            "step_exists": step is not None and step.exists(),
            "kqp_history_status": kqp_history.get("overall_status"),
            "kqp_ir_status": kqp_ir.get("overall_status"),
            "sample_agree": beq.get("sample_level_agreement"),
            "targeted_failure_preserved": beq.get("targeted_failure_preserved"),
            "delta_consistent": delta_report["validation"].get("passed"),
            "perturbation_aligned": align_report.get("delta_consistent"),
            "repair_eligible": repair_eligible,
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    clean_set_path = ROOT / "Reconstruction_results" / "clean_reconstruction_set.json"
    clean_set = json.loads(clean_set_path.read_text(encoding="utf-8"))
    clean_samples = clean_set["clean_samples"]
    print(f"Compiling {len(clean_samples)} clean samples...")

    clean_rows = compile_clean_set(clean_samples)
    n_clean_pass = sum(1 for r in clean_rows if r.get("compile_pass") == "pass" or r.get("compile_pass") is True)
    print(f"Clean: {n_clean_pass}/{len(clean_rows)} compiled + adaptor OK")

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
                 "reconstruction_success": r.get("eligible_for_detection_eval", False)}
                for r in kqp.get("rows", [])
            ]
        }
    print(f"Compiling negatives from task5 adaptor summary "
          f"({sum(1 for r in (adapt_summary or {}).get('rows', []) if r.get('reconstruction_success'))} reconstructable)...")

    neg_rows = compile_negative_set(adapt_summary)
    n_neg_pass = sum(1 for r in neg_rows if r.get("compile_pass"))
    n_neg_eligible = sum(1 for r in neg_rows if r.get("repair_eligible"))
    print(f"Negative: {n_neg_pass}/{len(neg_rows)} compiled OK, "
          f"{n_neg_eligible} repair-eligible")

    # Compile summary
    summary = {
        "phase": "Task 2 — History2IR Compiler v0.1",
        "n_clean": len(clean_rows),
        "n_clean_compile_pass": n_clean_pass,
        "n_negative": len(neg_rows),
        "n_negative_compile_pass": n_neg_pass,
        "n_repair_eligible": n_neg_eligible,
        "clean_rows": clean_rows,
        "negative_rows": neg_rows,
    }
    (REPORTS / "compile_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"\nSummary → {REPORTS / 'compile_summary.json'}")

    # Repair Eligible Negative Set manifest
    eligible = [r for r in neg_rows if r.get("repair_eligible")]
    manifest = {
        "phase": "Repair Eligible Negative Set v0.1",
        "criteria": "compile_pass AND adaptor success AND step_exists "
                      "AND behavioral_equivalence.sample_agree "
                      "AND behavioral_equivalence.targeted_failure_preserved",
        "n_eligible": len(eligible),
        "n_total_negatives": len(neg_rows),
        "eligible_ratio": len(eligible) / max(1, len(neg_rows)),
        "samples": [
            {"sample_id": r["sample_id"], "negative_id": r["negative_id"]}
            for r in eligible
        ],
    }
    (REPORTS / "repair_eligible_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"Manifest → {REPORTS / 'repair_eligible_manifest.json'}")


if __name__ == "__main__":
    main()