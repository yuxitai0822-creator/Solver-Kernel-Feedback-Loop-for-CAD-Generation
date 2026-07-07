"""validate_perturbation.py — Verify a negative is actually different & meaningful.

Checks (all must pass for eligible_for_detection_eval):
  1. ReconstructionEngine succeeded (compile/exec/export/occt_load all True)
  2. perturbed STEP differs from original STEP (vertex count or bbox differs)
  3. KQP result shows at least one FAILED query
  4. expected_failed_query ids (or their intent-mates) are in failed list

Use
---
  validate_one(neg_dir, original_step, expected_query_ids)
returns a dict with perturb_valid + per-check details.

The function expects:
  * neg_dir/generated.step exists
  * neg_dir/reconstruction_report.json exists
  * neg_dir/kqp_result.json exists
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))


def occt_shape_signature(step_path):
    """Compact OCCT signature: bbox + n_vertices."""
    from step_loader import load_step
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_VERTEX
    shape, _ = load_step(step_path)
    if shape is None or shape.IsNull():
        return {"ok": False, "reason": "load_failed"}
    bbox = Bnd_Box()
    BRepBndLib.Add_s(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    n_v = 0
    ex = TopExp_Explorer(shape, TopAbs_VERTEX)
    while ex.More():
        n_v += 1
        ex.Next()
    return {
        "ok": True,
        "bbox": [round(xmin, 4), round(ymin, 4), round(zmin, 4),
                  round(xmax, 4), round(ymax, 4), round(zmax, 4)],
        "n_vertices": n_v,
    }


def safe_shape_signature(step_path):
    try:
        return occt_shape_signature(step_path)
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_signature_change(original_step, perturbed_step):
    sig0 = safe_shape_signature(original_step)
    sig1 = safe_shape_signature(perturbed_step)
    if not sig0.get("ok") or not sig1.get("ok"):
        return {"signature_extractable": False,
                "original": sig0, "perturbed": sig1}
    bbox_changed = sig0["bbox"] != sig1["bbox"]
    nv_changed = sig0["n_vertices"] != sig1["n_vertices"]
    return {
        "signature_extractable": True,
        "original": sig0,
        "perturbed": sig1,
        "bbox_changed": bbox_changed,
        "vertex_count_changed": nv_changed,
        "signature_different": bbox_changed or nv_changed,
    }


def collect_failed_query_ids(kqp_result):
    return sorted({qr.get("query_id") for qr in kqp_result.get("query_results", [])
                    if qr.get("status") == "fail"})


def validate_one(neg_dir: Path, original_step: Path,
                   expected_query_ids: list[str],
                   intent_alias: dict | None = None
                   ) -> dict:
    """Validate one perturbation's full output dir."""
    perturbed_step = neg_dir / "generated.step"
    rec_report_path = neg_dir / "reconstruction_report.json"
    kqp_res_path = neg_dir / "kqp_result.json"

    # Check 1: reconstruction
    rec_ok = False
    rec_report = {}
    if rec_report_path.exists():
        rec_report = json.loads(rec_report_path.read_text(encoding="utf-8"))
        rec_ok = (rec_report.get("compile_success")
                   and rec_report.get("execute_success")
                   and rec_report.get("export_success")
                   and rec_report.get("occt_load_success"))

    # Check 2: signature differs
    sig_change = check_signature_change(original_step, perturbed_step)
    geom_different = sig_change.get("signature_different", False)

    # Check 3: KQP result
    kqp_res = {}
    if kqp_res_path.exists():
        kqp_res = json.loads(kqp_res_path.read_text(encoding="utf-8"))
    failed_ids = collect_failed_query_ids(kqp_res)
    any_failed = bool(failed_ids)

    # Check 4: expected query ids OR their aliases appear in failed list
    expected_in_failed = [q for q in expected_query_ids if q in failed_ids]
    target_intent_map = intent_alias or {}
    intent_in_failed = []
    for qid in expected_query_ids:
        intent = target_intent_map.get(qid)
        if intent and intent in [qr.get("intent") for qr in kqp_res.get("query_results", [])
                                   if qr.get("status") == "fail"]:
            intent_in_failed.append(qid)

    expected_resolved = set(expected_in_failed) | set(intent_in_failed)

    return {
        "perturbation_valid": rec_ok and geom_different and any_failed,
        "eligible_for_detection_eval": (rec_ok and geom_different
                                          and bool(expected_resolved)),
        "reconstruction_success": rec_ok,
        "reconstruction_report": rec_report,
        "signature_change_check": sig_change,
        "kqp_check": {
            "expected_failed_present": sorted(expected_in_failed),
            "expected_intent_present": sorted(intent_in_failed),
            "expected_failed_missing": sorted(set(expected_query_ids) - expected_resolved),
            "all_failed_query_ids": failed_ids,
        },
        "any_query_failed": any_failed,
        "expected_query_ids": expected_query_ids,
    }
