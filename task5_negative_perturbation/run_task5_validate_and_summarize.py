"""run_task5_validate_and_summarize.py — Run perturbation validity check and
produce Task5 summary metrics (NDR / TQDR / FPR / Diagnostic / Category).

For each perturbation <sid>/<neg_id>:
  1. Validate (signatures, expected failure)
  2. Compute per-negative metrics: detected? targeted? all_pass? diagnostic ok?
  3. Aggregate per error category and target intent
  4. Write summary reports
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "task5_negative_perturbation" / "perturbation"))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))


from perturbation.validate_perturbation import validate_one, collect_failed_query_ids


PERT_DIR = ROOT / "task5_negative_perturbation" / "perturbations"
HISTORY_DIR_FALLBACK = ROOT / "Reconstruction_results"
KQP_DIR = ROOT / "kqp" / "outputs" / "compiler_v0.1"
REPORTS_DIR = ROOT / "task5_negative_perturbation" / "reports"


def _original_step(sid):
    return HISTORY_DIR_FALLBACK / sid / "generated.step"


def _safe_load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def query_intent_map(kqp):
    """Return mapping query_id -> intent."""
    return {q["id"]: q.get("intent", "") for q in kqp.get("queries", [])}


def diagnostic_ok(qr):
    """Check that a fail query result has the required feedback fields."""
    fb = qr.get("feedback")
    if not isinstance(fb, dict):
        return False
    for key in ("error_type", "message"):
        if key not in fb or fb[key] is None or fb[key] == "":
            return False
    return True


def compute_metrics_one(sample_id: str, neg_id: str) -> dict:
    sid = sample_id
    neg_dir = PERT_DIR / sid / neg_id
    meta_path = neg_dir / "perturbation_meta.json"
    if not meta_path.exists():
        return {"missing_meta": True}
    meta = _safe_load(meta_path)

    expected_query_ids = meta.get("expected_query_ids_resolved") or []
    target_intent = meta.get("target_intent") or ""

    kqp_path = KQP_DIR / f"{sid}.kqp_instance.json"
    kqp = _safe_load(kqp_path) if kqp_path.exists() else {}
    intent_map = query_intent_map(kqp)

    # Map expected query ids -> expected intent if missing target_intent.
    if not target_intent and expected_query_ids:
        for q in expected_query_ids:
            target_intent = intent_map.get(q, "")
            if target_intent:
                break

    # KQP result
    kqp_res_path = neg_dir / "kqp_result.json"
    kqp_res = _safe_load(kqp_res_path) if kqp_res_path.exists() else {}

    failed_ids = collect_failed_query_ids(kqp_res)
    any_failed = bool(failed_ids)

    # TQDR: per-target expected query — does the intent-mate fail?
    # In sampler we may have listed "q_bbox_u" or "q_bbox_v"; only the
    # relevant one matches the axis we perturbed.  Use intent match.
    targeted_query_failed_ids = []
    for qid in expected_query_ids:
        if qid in failed_ids:
            targeted_query_failed_ids.append(qid)
    if not targeted_query_failed_ids:
        # Fallback: any failed query has the target intent
        for qr in kqp_res.get("query_results", []):
            if (qr.get("status") == "fail"
                    and qr.get("intent") == target_intent):
                targeted_query_failed_ids.append(qr["query_id"])
    tqdr_pass = bool(targeted_query_failed_ids)

    # Diagnostic completeness: every failed query has full feedback
    diag_ok = True
    diag_fail_query_ids = []
    for qr in kqp_res.get("query_results", []):
        if qr.get("status") == "fail":
            if not diagnostic_ok(qr):
                diag_ok = False
                diag_fail_query_ids.append(qr["query_id"])

    # Validity (reconstruction + signature + a query failed)
    original_step = _original_step(sid)
    validity = None
    if original_step.exists():
        try:
            validity = validate_one(neg_dir, original_step,
                                      expected_query_ids,
                                      intent_alias=intent_map)
        except Exception as e:
            validity = {"validate_exception": str(e)}

    rec_ok = False
    sig_diff = False
    if validity:
        rec_ok = validity.get("reconstruction_success", False)
        sig_diff = validity.get("signature_change_check", {}).get(
            "signature_different", False)

    # Per spec: eligible_for_detection_eval = rec_ok + sig_diff (perturbation
    # is real and produced a different STEP).  KQP success/failure is
    # what NDR / TQDR / FPR measure on top of that.
    eligible = bool(rec_ok and sig_diff)

    return {
        "sample_id": sid,
        "negative_id": neg_id,
        "operator": meta.get("operator_input_name"),
        "error_category": meta.get("error_category"),
        "target_intent": target_intent,
        "expected_query_ids": expected_query_ids,
        "expected_failed_intent": target_intent,
        "kqp_overall": kqp_res.get("overall_status"),
        "kqp_n_queries": kqp_res.get("summary", {}).get("total_queries"),
        "kqp_n_passed": kqp_res.get("summary", {}).get("passed_queries"),
        "kqp_n_failed": kqp_res.get("summary", {}).get("failed_queries"),
        "kqp_failed_query_ids": failed_ids,
        "any_query_failed": any_failed,
        "targeted_query_failed_ids": targeted_query_failed_ids,
        "targeted": tqdr_pass,
        "all_pass_negatives": (eligible and not any_failed),
        "diagnostic_complete": diag_ok,
        "diagnostic_fail_query_ids": diag_fail_query_ids,
        "eligible_for_detection_eval": eligible,
        "perturbation_validity": validity,
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for sample_dir in sorted(PERT_DIR.iterdir()):
        if not sample_dir.is_dir():
            continue
        sid = sample_dir.name
        for neg_dir in sorted(sample_dir.iterdir()):
            if not neg_dir.is_dir():
                continue
            neg_id = neg_dir.name
            rows.append(compute_metrics_one(sid, neg_id))

    # Aggregates
    eligible_rows = [r for r in rows if r.get("eligible_for_detection_eval")]
    detected = [r for r in eligible_rows if r.get("any_query_failed")]
    targeted = [r for r in eligible_rows if r.get("targeted")]
    diagnostic_ok = [r for r in eligible_rows if r.get("diagnostic_complete")]
    all_pass = [r for r in eligible_rows if r.get("all_pass_negatives")]

    n_eligible = len(eligible_rows)
    ndr = (len(detected) / n_eligible) if n_eligible else 0.0
    tqdr = (len(targeted) / n_eligible) if n_eligible else 0.0
    fpr = (len(all_pass) / n_eligible) if n_eligible else 0.0
    diag_rate = (len(diagnostic_ok) / n_eligible) if n_eligible else 0.0

    # Category detection rate
    cat: dict[str, dict] = {}
    for r in eligible_rows:
        ec = r.get("error_category") or "unknown"
        c = cat.setdefault(ec, {"eligible": 0, "detected": 0, "targeted": 0})
        c["eligible"] += 1
        if r.get("any_query_failed"):
            c["detected"] += 1
        if r.get("targeted"):
            c["targeted"] += 1
    for ec, c in cat.items():
        c["detection_rate"] = (c["detected"] / c["eligible"]) if c["eligible"] else 0.0
        c["tqdr_rate"] = (c["targeted"] / c["eligible"]) if c["eligible"] else 0.0

    # Intent-level
    intent_stats: dict[str, dict] = {}
    for r in eligible_rows:
        ti = r.get("target_intent") or "unknown"
        d = intent_stats.setdefault(ti, {"eligible": 0, "detected": 0, "targeted": 0,
                                           "all_pass": 0})
        d["eligible"] += 1
        if r.get("any_query_failed"):
            d["detected"] += 1
        if r.get("targeted"):
            d["targeted"] += 1
        if r.get("all_pass_negatives"):
            d["all_pass"] += 1
    for ti, d in intent_stats.items():
        d["detection_rate"] = (d["detected"] / d["eligible"]) if d["eligible"] else 0.0
        d["tqdr_rate"] = (d["targeted"] / d["eligible"]) if d["eligible"] else 0.0
        d["all_pass_rate"] = (d["all_pass"] / d["eligible"]) if d["eligible"] else 0.0

    summary = {
        "phase": "Task 5 Negative-Perturbation Detection",
        "total_rows": len(rows),
        "n_eligible": n_eligible,
        "n_detected_any": len(detected),
        "n_targeted": len(targeted),
        "n_all_pass": len(all_pass),
        "n_diagnostic_complete": len(diagnostic_ok),
        "NDR": ndr,
        "TQDR": tqdr,
        "FPR": fpr,
        "DiagnosticCompleteness": diag_rate,
        "by_error_category": cat,
        "by_target_intent": intent_stats,
        "rows": rows,
    }

    (REPORTS_DIR / "kqp_detection_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"=== Task5 Detection Summary ===")
    print(f"N_eligible: {n_eligible} / {len(rows)} total")
    print(f"NDR = {ndr:.2%}")
    print(f"TQDR = {tqdr:.2%}")
    print(f"FPR = {fpr:.2%}")
    print(f"Diagnostic Completeness = {diag_rate:.2%}")
    print(f"\nBy error category:")
    for ec, c in sorted(cat.items()):
        print(f"  {ec}: eligible={c['eligible']}, detected={c['detected']}, "
              f"det_rate={c['detection_rate']:.2%}")
    print(f"\nBy target intent:")
    for ti, d in sorted(intent_stats.items()):
        print(f"  {ti}: eligible={d['eligible']}, detected={d['detected']}, "
              f"det_rate={d['detection_rate']:.2%}, "
              f"all_pass={d['all_pass']}")

    # Write false pass case report
    fp_md = []
    fp_md.append("# False Pass Cases in Task5\n")
    fp_md.append(f"Total false passes: {len(all_pass)} / eligible {n_eligible}\n\n")
    if all_pass:
        fp_md.append("| sample_id | negative_id | operator | target_intent |\n")
        fp_md.append("|---|---|---|---|\n")
        for r in all_pass:
            fp_md.append(f"| {r['sample_id']} | {r['negative_id']} | "
                          f"{r.get('operator')} | {r.get('target_intent')} |\n")
    (REPORTS_DIR / "false_pass_cases.md").write_text("".join(fp_md),
                                                       encoding="utf-8")


if __name__ == "__main__":
    main()
