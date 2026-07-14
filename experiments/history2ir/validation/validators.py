"""validators.py — Validators for the History2IR Compiler.

Five validators (per task spec §11):
  1. Schema Validation     — cad_ir_v0.1 schema check
  2. Semantic Validation   — domain constraints
  3. Delta Consistency     — diff(clean_ir, neg_ir) matches perturbation_meta
  4. Behavioral Equivalence — IR-execution KQP matches Reconstruction KQP
  5. Perturbation Alignment — IR field-level alignment with perturbation meta

Each validator returns a dict {passed: bool, issues: [str, ...], ...}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
import importlib
_validate_mod = importlib.import_module("cad_ir.validator.validator")
cad_ir_validate = _validate_mod.validate


# ---------------------------------------------------------------------------
# 1. Schema validation
# ---------------------------------------------------------------------------

def validate_schema(ir: dict) -> dict:
    """Validate against cad_ir_v0.1 schema (schema + semantic)."""
    res = cad_ir_validate(ir, semantic=True)
    return {
        "passed": res["overall"] == "pass",
        "schema_status": res["schema_status"],
        "semantic_status": res["semantic_status"],
        "issues": res["schema_issues"] + res["semantic_issues"],
    }


# ---------------------------------------------------------------------------
# 2. Semantic validation (extra, History2IR-specific)
# ---------------------------------------------------------------------------

def validate_semantic_history2ir(ir: dict) -> dict:
    """History2IR-specific semantic checks beyond cad_ir_v0.1."""
    issues: list[str] = []
    opids: set[str] = set()
    for op in ir.get("operations", []):
        oid = op.get("op_id")
        if oid in opids:
            issues.append(f"duplicate op_id: {oid}")
        opids.add(oid)
        # Reference resolution
        for ref in (op.get("input"), op.get("role")):
            if ref is None:
                continue
            if ref in opids:
                continue
            if ref in ("base_profile", "base_body", "boolean_op", "export"):
                continue  # role strings
            # Otherwise ref should be a uuid or op_id; we leave it as warning
        # Input dependency exists
        ref = op.get("input")
        if ref is not None and ref not in opids:
            # Could be a uuid not yet converted; OK
            if not all(c in "0123456789abcdef-" for c in ref):
                issues.append(f"op {oid} has unknown input ref: {ref}")
    return {"passed": not issues, "issues": issues}


# ---------------------------------------------------------------------------
# 3. Delta Consistency: diff(IR_clean, IR_neg) ↔ perturbation_meta
# ---------------------------------------------------------------------------

def validate_delta_consistency(ir_clean: dict, ir_neg: dict,
                                  perturbation_meta: dict) -> dict:
    """Verify that the IR delta matches the perturbation metadata.

    Approach: find the affected op (by operator, original_value,
    perturbed_value), then check the IR has the same field delta.
    """
    issues: list[str] = []
    op_input_name = perturbation_meta.get("operator_input_name", "")
    original = perturbation_meta.get("original_value")
    perturbed = perturbation_meta.get("perturbed_value")
    target_intent = perturbation_meta.get("target_intent", "")

    # Map operator → IR parameter
    op_to_field = {
        "E1_envelope_u": ("sketch_rectangle", "width"),
        "E1_envelope_v": ("sketch_rectangle", "height"),
        "E1_envelope_u_shrink": ("sketch_rectangle", "width"),
        "E1_envelope_v_shrink": ("sketch_rectangle", "height"),
        "E2_extrude_deep": ("extrude", "distance"),
        "E2_extrude_shallow": ("extrude", "distance"),
        "E3_radius_up": ("sketch_circle", "radius"),
        "E3_radius_down": ("sketch_circle", "radius"),
        "E3_inner_radius_up": ("sketch_annulus", "inner_radius"),
        "E3_inner_radius_down": ("sketch_annulus", "inner_radius"),
    }
    target_op_type, target_field = op_to_field.get(
        op_input_name, (None, None))

    found_match = False
    for op in ir_neg.get("operations", []):
        if op.get("op_type") == target_op_type:
            if target_field and target_field in op.get("params", {}):
                actual_perturbed = op["params"][target_field]
                if perturbed is not None and actual_perturbed is not None:
                    # Compare in cm vs mm
                    if abs(float(actual_perturbed) - float(perturbed) * 10) > 0.5:
                        issues.append(
                            f"perturbed value mismatch: IR has {actual_perturbed}, "
                            f"meta has {perturbed} (× 10 = {perturbed * 10})")
                    else:
                        found_match = True
                    break
                if actual_perturbed is not None:
                    found_match = True
                    break

    if not found_match:
        issues.append(
            f"could not locate {target_op_type}/{target_field} in IR "
            f"to match perturbation {op_input_name}")

    # Cross-validate by comparing IR_clean vs IR_neg for the same field
    if target_op_type and target_field:
        for op in ir_clean.get("operations", []):
            if op.get("op_type") == target_op_type:
                if target_field in op.get("params", {}):
                    clean_val = op["params"][target_field]
                    # Find matching neg op
                    for nop in ir_neg.get("operations", []):
                        if nop.get("op_type") == target_op_type \
                                and target_field in nop.get("params", {}):
                            neg_val = nop["params"][target_field]
                            if original is not None and clean_val is not None:
                                if abs(float(clean_val) - float(original) * 10) > 0.5:
                                    issues.append(
                                        f"clean IR value mismatch: {clean_val} vs "
                                        f"meta {original} (× 10 = {original*10})")
                            break
                    break

    return {
        "passed": not issues,
        "issues": issues,
        "found_match": found_match,
        "target_op_type": target_op_type,
        "target_field": target_field,
    }


# ---------------------------------------------------------------------------
# 4. Perturbation Alignment: report-style delta for inspection
# ---------------------------------------------------------------------------

def compute_perturbation_alignment_report(ir_clean: dict, ir_neg: dict,
                                            perturbation_meta: dict) -> dict:
    """Build a structured report of where the IR preserves the perturbation."""
    op_input_name = perturbation_meta.get("operator_input_name", "")
    report = {
        "sample_id": perturbation_meta.get("sample_id"),
        "negative_id": perturbation_meta.get("negative_id"),
        "perturbation_type": op_input_name,
        "history_delta": {
            "entity_id": perturbation_meta.get("modified_history_field"),
            "field": op_input_name,
            "before": perturbation_meta.get("original_value"),
            "after": perturbation_meta.get("perturbed_value"),
        },
        "ir_delta": {"operation_id": None, "field": None,
                       "before": None, "after": None},
        "target_operation_match": False,
        "target_field_match": False,
        "before_value_match": False,
        "after_value_match": False,
        "delta_consistent": False,
    }
    op_to_field = {
        "E2_extrude_deep": ("extrude", "distance"),
        "E2_extrude_shallow": ("extrude", "distance"),
        "E1_envelope_u": ("sketch_rectangle", "width"),
        "E1_envelope_v": ("sketch_rectangle", "height"),
        "E1_envelope_u_shrink": ("sketch_rectangle", "width"),
        "E1_envelope_v_shrink": ("sketch_rectangle", "height"),
        "E3_radius_up": ("sketch_circle", "radius"),
        "E3_radius_down": ("sketch_circle", "radius"),
        "E3_inner_radius_up": ("sketch_annulus", "inner_radius"),
        "E3_inner_radius_down": ("sketch_annulus", "inner_radius"),
    }
    target_op_type, target_field = op_to_field.get(op_input_name, (None, None))
    if not target_op_type:
        return report
    for op_clean, op_neg in zip(ir_clean.get("operations", []),
                                     ir_neg.get("operations", [])):
        if (op_clean.get("op_type") == target_op_type
                and op_neg.get("op_type") == target_op_type
                and target_field in op_clean.get("params", {})
                and target_field in op_neg.get("params", {})):
            report["ir_delta"] = {
                "operation_id": op_neg.get("op_id"),
                "field": target_field,
                "before": op_clean["params"][target_field],
                "after": op_neg["params"][target_field],
            }
            report["target_operation_match"] = True
            report["target_field_match"] = True
            # cm vs mm scaling
            b = perturbation_meta.get("original_value")
            a = perturbation_meta.get("perturbed_value")
            if b is not None:
                report["before_value_match"] = (
                    abs(op_clean["params"][target_field] - b * 10) < 0.5)
            if a is not None:
                report["after_value_match"] = (
                    abs(op_neg["params"][target_field] - a * 10) < 0.5)
            report["delta_consistent"] = (
                report["target_operation_match"]
                and report["target_field_match"]
                and report["before_value_match"]
                and report["after_value_match"])
            break
    return report


# ---------------------------------------------------------------------------
# 5. Behavioral Equivalence: IR-execution KQP vs Reconstruction KQP
# ---------------------------------------------------------------------------

def compare_kqp_equivalence(kqp_history: dict, kqp_ir: dict) -> dict:
    """Compare two KQP feedback dicts for status agreement."""
    if not kqp_history or not kqp_ir:
        return {"sample_level_agreement": False,
                "query_level_agreement": 0.0,
                "targeted_failure_preserved": False,
                "history_signature": [],
                "ir_signature": [],
                "issues": ["missing KQP feedback"]}
    # Sample-level
    s_hist = kqp_history.get("overall_status", "unknown") == "pass"
    s_ir = kqp_ir.get("overall_status", "unknown") == "pass"
    sample_agree = (s_hist == s_ir)

    # Query-level
    qr_hist = {qr.get("query_id"): qr for qr in kqp_history.get("query_results", [])}
    qr_ir = {qr.get("query_id"): qr for qr in kqp_ir.get("query_results", [])}
    common_qs = set(qr_hist) & set(qr_ir)
    if not common_qs:
        return {"sample_level_agreement": sample_agree,
                "query_level_agreement": 0.0,
                "targeted_failure_preserved": False,
                "history_signature": list(qr_hist.keys()),
                "ir_signature": list(qr_ir.keys()),
                "issues": ["no common query ids"]}
    agree = sum(1 for qid in common_qs
                  if qr_hist[qid].get("status") == qr_ir[qid].get("status"))
    q_agreement = agree / len(common_qs)

    # Targeted failure preservation
    target_qids = set()
    expected_failed = kqp_history.get("targeted_query_failed_ids") or []
    expected_failed = set(expected_failed) if isinstance(expected_failed, list) else set()
    if not expected_failed:
        # Fall back: any query that failed in history
        for qid, qr in qr_hist.items():
            if qr.get("status") == "fail":
                expected_failed.add(qid)
    target_qids = expected_failed
    targeted_preserved = True
    for qid in target_qids:
        if qid not in qr_ir:
            targeted_preserved = False
            continue
        if qr_ir[qid].get("status") != "fail":
            targeted_preserved = False

    issues = []
    if not sample_agree:
        issues.append(f"sample-level disagreement: history {s_hist} vs IR {s_ir}")
    if q_agreement < 0.95:
        issues.append(f"query-level agreement {q_agreement:.2%} < 95%")

    return {
        "sample_level_agreement": sample_agree,
        "query_level_agreement": q_agreement,
        "targeted_failure_preserved": targeted_preserved,
        "history_signature": [qr.get("query_id")
                                 for qr in kqp_history.get("query_results", [])
                                 if qr.get("status") == "fail"],
        "ir_signature": [qr.get("query_id")
                             for qr in kqp_ir.get("query_results", [])
                             if qr.get("status") == "fail"],
        "issues": issues,
    }
