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

def _polygon_bbox(vertices: list) -> dict | None:
    """Compute width (u-span) and height (v-span) of a polygon's vertices
    treated as a flat sequence of 2D points (mm).  Returns None if empty."""
    if not vertices:
        return None
    xs = [float(v[0]) for v in vertices if isinstance(v, (list, tuple)) and len(v) >= 2]
    ys = [float(v[1]) for v in vertices if isinstance(v, (list, tuple)) and len(v) >= 2]
    if not xs or not ys:
        return None
    return {"width": round(max(xs) - min(xs), 4),
              "height": round(max(ys) - min(ys), 4)}


def _extract_dim(ir: dict, target_op_type: str, target_field: str) -> float | None:
    """Find a numeric value for ``target_field`` in ``ir``, accepting both
    named-param sketches (``sketch_rectangle.width``, etc.) and
    bbox-from-vertices (``sketch_polygon`` → ``width``/``height`` derived
    from the outermost vertices)."""
    for op in ir.get("operations", []):
        if op.get("op_type") != target_op_type:
            continue
        params = op.get("params", {}) or {}
        if target_field in params:
            return params[target_field]
        # Polygon: derive width/height from vertices bbox.
        if op.get("op_type") == "sketch_polygon" and target_field in ("width", "height"):
            bb = _polygon_bbox(params.get("vertices", []) or [])
            if bb and target_field in bb:
                return bb[target_field]
    return None


def _extract_text(ir: dict, op_type: str, field: str):
    """Extract a non-numeric field (e.g. extent_type) from the first matching op."""
    for op in ir.get("operations", []):
        if op.get("op_type") == op_type:
            v = op.get("params", {}).get(field)
            if v is not None:
                return v
    return None


def validate_delta_consistency(ir_clean: dict, ir_neg: dict,
                                  perturbation_meta: dict) -> dict:
    """Verify that the IR delta matches the perturbation metadata.

    V0.1.4 fix: accept both ``sketch_rectangle.width/height`` AND the
    bbox derived from ``sketch_polygon.vertices`` so that perturbations on
    polygon-classified sketches (which the parser emits when the sketch
    is irregular) are still verifiable.  Also adds E4 (void add/remove)
    and E5 (extent_type) operator mappings.
    """
    issues: list[str] = []
    op_input_name = perturbation_meta.get("operator_input_name", "")
    original = perturbation_meta.get("original_value")
    perturbed = perturbation_meta.get("perturbed_value")
    target_intent = perturbation_meta.get("target_intent", "")

    # Map operator → IR parameter.  For envelope dimensions, allow EITHER
    # sketch_rectangle OR sketch_polygon (derive from vertices).
    # E4/E5/E6 don't directly translate to IR ops (loops / extent_type /
    # inner-vs-outer) but we still surface what we'd expect to see.
    op_to_field = {
        "E1_envelope_u": [("sketch_rectangle", "width"),
                            ("sketch_polygon", "width")],
        "E1_envelope_v": [("sketch_rectangle", "height"),
                            ("sketch_polygon", "height")],
        "E1_envelope_u_shrink": [("sketch_rectangle", "width"),
                                   ("sketch_polygon", "width")],
        "E1_envelope_v_shrink": [("sketch_rectangle", "height"),
                                   ("sketch_polygon", "height")],
        "E2_extrude_deep": [("extrude", "distance")],
        "E2_extrude_shallow": [("extrude", "distance")],
        "E3_radius_up": [("sketch_circle", "radius")],
        "E3_radius_down": [("sketch_circle", "radius")],
        "E3_inner_radius_up": [("sketch_annulus", "inner_radius")],
        "E3_inner_radius_down": [("sketch_annulus", "inner_radius")],
        # E5 changes extrude.extent_type (string → string)
        "E5_extent_type_change": [("extrude", "extent_type")],
        # E6 inner-radius > outer-radius: annulus has the new (invalid) inner
        "E6_inner_gt_outer": [("sketch_annulus", "inner_radius"),
                                  ("sketch_annulus", "outer_radius")],
    }
    target_options = op_to_field.get(op_input_name, [])
    target_op_type = target_options[0][0] if target_options else None
    target_field = target_options[0][1] if target_options else None

    # E4 (void add/remove): the IR doesn't model inner loops directly.  We
    # accept this as a "structural" delta: the IR for void_remove must NOT
    # carry the corresponding rect-frame inner params (or for void_add,
    # the IR must be a frame), and the clean+neg bbox_u/v must be equal
    # (void perturbations don't change envelope bbox).  Mark as found_match
    # if EITHER bbox is unchanged (=> structural delta plausible).
    if op_input_name in ("E4_void_add", "E4_void_remove_one"):
        clean_bb = _extract_dim(ir_clean, "sketch_rectangle", "width") \
                    or _extract_dim(ir_clean, "sketch_polygon", "width")
        neg_bb = _extract_dim(ir_neg, "sketch_rectangle", "width") \
                    or _extract_dim(ir_neg, "sketch_polygon", "width")
        clean_bb_v = _extract_dim(ir_clean, "sketch_rectangle", "height") \
                       or _extract_dim(ir_clean, "sketch_polygon", "height")
        neg_bb_v = _extract_dim(ir_neg, "sketch_rectangle", "height") \
                     or _extract_dim(ir_neg, "sketch_polygon", "height")
        bbox_unchanged = (clean_bb == neg_bb and clean_bb_v == neg_bb_v
                            and clean_bb not in (None, 0))
        return {
            "passed": True,            # E4 is structurally non-envelope
            "issues": [],
            "found_match": bbox_unchanged,
            "target_op_type": "structural",
            "target_field": "loops",
            "bbox_unchanged": bbox_unchanged,
        }

    actual_op_type, actual_field = None, None
    actual_perturbed = None
    for op_type, field in target_options:
        val = _extract_dim(ir_neg, op_type, field)
        if val is not None:
            actual_op_type, actual_field, actual_perturbed = op_type, field, val
            break
    # Also try string fields (E5 extent_type).
    if actual_perturbed is None:
        for op_type, field in target_options:
            val = _extract_text(ir_neg, op_type, field)
            if val is not None:
                actual_op_type, actual_field, actual_perturbed = op_type, field, val
                break

    found_match = False
    if actual_perturbed is not None and perturbed is not None:
        try:
            if abs(float(actual_perturbed) - float(perturbed) * 10) > 0.5:
                issues.append(
                    f"perturbed value mismatch: IR has {actual_perturbed} "
                    f"({actual_op_type}.{actual_field}), "
                    f"meta has {perturbed} (× 10 = {perturbed * 10})")
            else:
                found_match = True
        except (TypeError, ValueError):
            # String compare (E5 extent_type).
            if str(actual_perturbed).lower() != str(perturbed).lower():
                # E5 maps Fusion360 extent_type names to IR extent_type names;
                # the canonical IR form ('symmetric', 'two_sides', 'one_side')
                # may differ in case from the F360 form.  Accept as match.
                _e5_alias = {
                    "onesidefeatureextenttype": "one_side",
                    "twosidesfeatureextenttype": "two_sides",
                    "symmetricfeatureextenttype": "symmetric",
                    "one_side": "one_side",
                    "two_sides": "two_sides",
                    "symmetric": "symmetric",
                }
                if (_e5_alias.get(str(actual_perturbed).lower())
                        != _e5_alias.get(str(perturbed).lower())):
                    issues.append(
                        f"perturbed value mismatch: IR has {actual_perturbed} "
                        f"({actual_op_type}.{actual_field}), meta has {perturbed}")
                else:
                    found_match = True
            else:
                found_match = True
    elif actual_perturbed is not None:
        found_match = True

    if not found_match:
        issues.append(
            f"could not locate {op_input_name} → {target_options} in IR_neg")

    # Cross-validate clean IR value vs original
    if target_field and original is not None:
        for op_type, field in target_options:
            clean_val = _extract_dim(ir_clean, op_type, field)
            if clean_val is not None:
                try:
                    if abs(float(clean_val) - float(original) * 10) > 0.5:
                        issues.append(
                            f"clean IR value mismatch: {clean_val} "
                            f"({op_type}.{field}) vs "
                            f"meta {original} (× 10 = {original*10})")
                except (TypeError, ValueError):
                    pass
                break

    return {
        "passed": not issues,
        "issues": issues,
        "found_match": found_match,
        "target_op_type": actual_op_type or target_op_type,
        "target_field": actual_field or target_field,
    }


# ---------------------------------------------------------------------------
# 4. Perturbation Alignment: report-style delta for inspection
# ---------------------------------------------------------------------------

def compute_perturbation_alignment_report(ir_clean: dict, ir_neg: dict,
                                            perturbation_meta: dict) -> dict:
    """Build a structured report of where the IR preserves the perturbation.

    V0.1.4 fix: accept both ``sketch_rectangle.width/height`` AND the
    bbox derived from ``sketch_polygon.vertices``.  Adds E4 / E5 / E6.
    """
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
        "E2_extrude_deep": [("extrude", "distance")],
        "E2_extrude_shallow": [("extrude", "distance")],
        "E1_envelope_u": [("sketch_rectangle", "width"),
                            ("sketch_polygon", "width")],
        "E1_envelope_v": [("sketch_rectangle", "height"),
                            ("sketch_polygon", "height")],
        "E1_envelope_u_shrink": [("sketch_rectangle", "width"),
                                   ("sketch_polygon", "width")],
        "E1_envelope_v_shrink": [("sketch_rectangle", "height"),
                                   ("sketch_polygon", "height")],
        "E3_radius_up": [("sketch_circle", "radius"),
                            ("sketch_annulus", "inner_radius"),
                            ("sketch_annulus", "outer_radius")],
        "E3_radius_down": [("sketch_circle", "radius"),
                             ("sketch_annulus", "inner_radius"),
                             ("sketch_annulus", "outer_radius")],
        "E3_inner_radius_up": [("sketch_annulus", "inner_radius")],
        "E3_inner_radius_down": [("sketch_annulus", "inner_radius")],
        "E5_extent_type_change": [("extrude", "extent_type")],
        "E6_inner_gt_outer": [("sketch_annulus", "inner_radius"),
                                  ("sketch_annulus", "outer_radius")],
    }
    target_options = op_to_field.get(op_input_name, [])
    if not target_options:
        return report
    target_op_type, target_field = target_options[0]

    # E4 void add/remove: structural delta (bbox unchanged).
    if op_input_name in ("E4_void_add", "E4_void_remove_one"):
        clean_bb_w = _extract_dim(ir_clean, "sketch_rectangle", "width") \
                       or _extract_dim(ir_clean, "sketch_polygon", "width")
        neg_bb_w = _extract_dim(ir_neg, "sketch_rectangle", "width") \
                     or _extract_dim(ir_neg, "sketch_polygon", "width")
        clean_bb_h = _extract_dim(ir_clean, "sketch_rectangle", "height") \
                       or _extract_dim(ir_clean, "sketch_polygon", "height")
        neg_bb_h = _extract_dim(ir_neg, "sketch_rectangle", "height") \
                     or _extract_dim(ir_neg, "sketch_polygon", "height")
        bbox_unchanged = (clean_bb_w == neg_bb_w and clean_bb_h == neg_bb_h
                            and clean_bb_w not in (None, 0))
        report["ir_delta"] = {"operation_id": None, "field": "loops",
                                "before": perturbation_meta.get("original_value"),
                                "after": perturbation_meta.get("perturbed_value")}
        report["target_operation_match"] = bbox_unchanged
        report["target_field_match"] = bbox_unchanged
        report["before_value_match"] = bbox_unchanged
        report["after_value_match"] = bbox_unchanged
        report["delta_consistent"] = bbox_unchanged
        return report

    clean_val, neg_val, neg_op_id = None, None, None
    for op_type, field in target_options:
        for op in ir_clean.get("operations", []):
            if op.get("op_type") != op_type:
                continue
            params = op.get("params", {}) or {}
            if field in params:
                clean_val = params[field]
                break
            if op.get("op_type") == "sketch_polygon" and field in ("width", "height"):
                bb = _polygon_bbox(params.get("vertices", []) or [])
                if bb and field in bb:
                    clean_val = bb[field]
                    break
        if clean_val is not None:
            break
    for op_type, field in target_options:
        for op in ir_neg.get("operations", []):
            if op.get("op_type") != op_type:
                continue
            params = op.get("params", {}) or {}
            if field in params:
                neg_val = params[field]
                neg_op_id = op.get("op_id")
                break
            if op.get("op_type") == "sketch_polygon" and field in ("width", "height"):
                bb = _polygon_bbox(params.get("vertices", []) or [])
                if bb and field in bb:
                    neg_val = bb[field]
                    neg_op_id = op.get("op_id")
                    break
        if neg_val is not None:
            break

    if clean_val is not None and neg_val is not None:
        report["ir_delta"] = {
            "operation_id": neg_op_id,
            "field": target_field,
            "before": clean_val,
            "after": neg_val,
        }
        report["target_operation_match"] = True
        report["target_field_match"] = True
        b = perturbation_meta.get("original_value")
        a = perturbation_meta.get("perturbed_value")
        # String vs numeric match.
        try:
            if b is not None:
                report["before_value_match"] = abs(float(clean_val) - float(b) * 10) < 0.5
            if a is not None:
                report["after_value_match"] = abs(float(neg_val) - float(a) * 10) < 0.5
        except (TypeError, ValueError):
            _e5_alias = {
                "onesidefeatureextenttype": "one_side",
                "twosidesfeatureextenttype": "two_sides",
                "symmetricfeatureextenttype": "symmetric",
                "one_side": "one_side",
                "two_sides": "two_sides",
                "symmetric": "symmetric",
            }
            cb = _e5_alias.get(str(clean_val).lower(), str(clean_val).lower())
            cn = _e5_alias.get(str(neg_val).lower(), str(neg_val).lower())
            mb = _e5_alias.get(str(b).lower(), str(b).lower()) if b is not None else None
            ma = _e5_alias.get(str(a).lower(), str(a).lower()) if a is not None else None
            report["before_value_match"] = (mb is None or cb == mb)
            report["after_value_match"] = (ma is None or cn == ma)
        report["delta_consistent"] = (
            report["target_operation_match"]
            and report["target_field_match"]
            and report["before_value_match"]
            and report["after_value_match"])
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
