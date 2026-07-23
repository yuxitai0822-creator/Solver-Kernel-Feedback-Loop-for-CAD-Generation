"""compute_ced.py — Top-level CAD Editing Distance computation.

Three metrics per task spec:
  CED_text       — Levenshtein over raw IR JSON text
  CED_declared   — Weighted edit distance over declared op sequence
  CED_executed   — Weighted edit distance over runtime trace

All metrics are normalized to [0, 1] (clipped if raw value > 1).
Raw values are also saved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad_edit_distance"))

from normalize_ir import normalize_ir, total_weight  # noqa: E402
from op_matcher import match_ops  # noqa: E402
from edit_cost import match_cost  # noqa: E402


# ---------------------------------------------------------------------------
# Levenshtein (small dependency-free implementation)
# ---------------------------------------------------------------------------

def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            ins = cur[j] + 1
            delete = prev[j + 1] + 1
            sub = prev[j] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


# ---------------------------------------------------------------------------
# CED_text
# ---------------------------------------------------------------------------

def ced_text(ir_a, ir_b) -> dict:
    """Levenshtein over the raw IR text, normalized to [0, 1]."""
    if isinstance(ir_a, dict):
        text_a = json.dumps(ir_a, sort_keys=True, ensure_ascii=False)
    else:
        text_a = ir_a
    if isinstance(ir_b, dict):
        text_b = json.dumps(ir_b, sort_keys=True, ensure_ascii=False)
    else:
        text_b = ir_b

    raw = _levenshtein(text_a, text_b)
    max_len = max(len(text_a), len(text_b), 1)
    norm = raw / max_len
    clipped = min(1.0, norm)
    return {"raw": raw, "normalized": clipped,
              "text_a_len": len(text_a), "text_b_len": len(text_b)}


# ---------------------------------------------------------------------------
# CED_declared
# ---------------------------------------------------------------------------

def ced_declared(ir_a: dict, ir_b: dict) -> dict:
    """Weighted edit distance over declared op sequences."""
    try:
        norm_a = normalize_ir(ir_a)
        norm_b = normalize_ir(ir_b)
    except Exception as e:
        return {"error": f"normalize failed: {type(e).__name__}: {e}",
                "raw": float("inf"), "normalized": 1.0,
                "available": False}

    ops_a = norm_a["operations"]
    ops_b = norm_b["operations"]

    matches = match_ops(ops_a, ops_b)
    raw = sum(match_cost(m) for m in matches)

    weight_a = total_weight(ops_a)
    weight_b = total_weight(ops_b)
    base = max(weight_a, weight_b, 1)

    normalized = raw / base
    clipped = min(1.0, normalized)

    breakdown = {
        "n_matches_added": sum(1 for m in matches if m["match_kind"] == "added"),
        "n_matches_deleted": sum(1 for m in matches if m["match_kind"] == "deleted"),
        "n_matches_matched": sum(1 for m in matches if m["match_kind"] == "matched"),
        "by_kind": _breakdown_by_kind(matches),
        "match_pairs": _format_match_pairs(matches),
    }

    return {
        "raw": raw,
        "normalized": clipped,
        "weight_a": weight_a,
        "weight_b": weight_b,
        "base": base,
        "n_ops_a": len(ops_a),
        "n_ops_b": len(ops_b),
        "available": True,
        "breakdown": breakdown,
    }


def _breakdown_by_kind(matches: list[dict]) -> dict:
    bd: dict[str, dict[str, float]] = {}
    for m in matches:
        op_a = m.get("a_op") or {}
        op_b = m.get("b_op") or {}
        ot = op_a.get("op_type") or op_b.get("op_type") or "unknown"
        if ot not in bd:
            bd[ot] = {"added": 0, "deleted": 0, "matched": 0, "cost": 0.0}
        bd[ot][m["match_kind"]] = bd[ot].get(m["match_kind"], 0) + 1
        bd[ot]["cost"] += match_cost(m)
    return bd


def _format_match_pairs(matches: list[dict]) -> list[dict]:
    out = []
    for m in matches:
        a = m.get("a_op") or {}
        b = m.get("b_op") or {}
        out.append({
            "match_kind": m["match_kind"],
            "match_by": m["match_by"],
            "a_op_id": a.get("op_id"),
            "b_op_id": b.get("op_id"),
            "a_op_type": a.get("op_type"),
            "b_op_type": b.get("op_type"),
            "cost": round(match_cost(m), 3),
        })
    return out


# ---------------------------------------------------------------------------
# CED_executed
# ---------------------------------------------------------------------------

def ced_executed(trace_a: dict, trace_b: dict) -> dict:
    """Weighted edit distance over executed op traces."""
    def _norm(trace: dict) -> list[dict]:
        ops = trace.get("operations", [])
        out = []
        for op in ops:
            ot = op.get("op_type", "unknown")
            status = op.get("runtime_status", "unknown")
            out.append({
                "op_id": op.get("op_id"),
                "op_type": ot,
                "status": status,
                "base_weight": _weight(ot),
            })
        return out

    def _weight(ot: str) -> int:
        return {"sketch_rectangle": 2, "sketch_circle": 2,
                "sketch_annulus": 2, "sketch_rectangular_frame": 2,
                "sketch_stadium": 2, "sketch_polygon": 2,
                "extrude": 3, "cut": 4, "join": 4, "add_constraint": 2,
                "set_dimension": 2, "export_step": 1}.get(ot, 3)

    ops_a = _norm(trace_a)
    ops_b = _norm(trace_b)
    matches = match_ops(ops_a, ops_b)
    raw = sum(match_cost(m) for m in matches)
    weight_a = sum(op["base_weight"] for op in ops_a)
    weight_b = sum(op["base_weight"] for op in ops_b)
    base = max(weight_a, weight_b, 1)
    normalized = raw / base
    clipped = min(1.0, normalized)
    return {"raw": raw, "normalized": clipped,
              "weight_a": weight_a, "weight_b": weight_b,
              "base": base,
              "n_ops_a": len(ops_a), "n_ops_b": len(ops_b)}


# ---------------------------------------------------------------------------
# Combined entry
# ---------------------------------------------------------------------------

def _ops_to_ir_dicts(ops: list) -> list[dict]:
    """Convert a list of code2oper ``Operation`` objects to the IR
    dict-list shape expected by ``match_ops`` and ``match_cost``.
    The IR-path normaliser (``normalize_ir``) produces these field
    names; we mimic them here.
    """
    # Mirror the v0.1 IR compiler's ``base_weight`` table.
    BASE_WEIGHTS = {
        "rectangle": 2.0, "circle": 1.5, "line": 0.5, "polygon": 1.5,
        "arc": 1.0,
        "extrude": 3.0, "cut": 3.0, "union": 1.0, "shell": 1.0,
        "fillet": 1.0,
        "translate": 0.5, "rotate": 0.5, "mirror": 0.5,
    }
    irs = []
    for i, op in enumerate(ops):
        op_type = op.operation
        op_id = f"op_{i+1:03d}"
        params = dict(op.parameters)
        irs.append({
            "op_id": op_id,
            "op_type": op_type,
            "parameters": params,
            "params_normalized": params,
            "base_weight": BASE_WEIGHTS.get(op_type, 1.0),
            "connections": {},
            "source": dict(op.source),
        })
    return irs


def ced_declared_ops(ops_a: list, ops_b: list) -> dict:
    """Weighted edit distance over two Operation lists (from code2oper).

    This is the v0.2-adapter for compute_ced.ced_declared: it accepts
    the structured operation lists produced by ``code2oper.parse`` rather
    than full IR dicts.  The weight model and match-cost model are
    identical to the IR-path version; only the input representation
    changes.
    """
    irs_a = _ops_to_ir_dicts(ops_a)
    irs_b = _ops_to_ir_dicts(ops_b)
    matches = match_ops(irs_a, irs_b)
    raw = sum(match_cost(m) for m in matches)
    weight_a = total_weight(irs_a)
    weight_b = total_weight(irs_b)
    base = max(weight_a, weight_b, 1)
    normalized = raw / base
    clipped = min(1.0, normalized)
    breakdown = {
        "n_matches_added": sum(1 for m in matches if m["match_kind"] == "added"),
        "n_matches_deleted": sum(1 for m in matches if m["match_kind"] == "deleted"),
        "n_matches_matched": sum(1 for m in matches if m["match_kind"] == "matched"),
        "by_kind": _breakdown_by_kind(matches),
        "match_pairs": _format_match_pairs(matches),
    }
    return {
        "raw": raw,
        "normalized": clipped,
        "weight_a": weight_a,
        "weight_b": weight_b,
        "base": base,
        "n_ops_a": len(ops_a),
        "n_ops_b": len(ops_b),
        "available": True,
        "breakdown": breakdown,
    }


def ced_with_fallback(ops_a: list | None, ops_b: list | None,
                        script_a: str | None = None,
                        script_b: str | None = None) -> dict:
    """Phase 2A R3 wrapper:  compute CED on Operation lists when both
    are parseable; fall back to CED_text (Levenshtein on the script
    source) when one or both are unparseable.

    Returns a single result dict with:
        parsed         : bool  (both ops lists valid)
        ced_declared   : dict | None   (None if not parseable)
        ced_text       : dict           (always present)
        primary_metric : "ced_declared" or "ced_text"
        primary_value  : float in [0, 1]
        primary_raw    : int
        parse_coverage : bool
    """
    parsed_a = ops_a is not None
    parsed_b = ops_b is not None
    parseable = parsed_a and parsed_b
    ced_declared_result = None
    if parseable:
        ced_declared_result = ced_declared_ops(ops_a, ops_b)
    # CED_text on the script text (always available).  We import the
    # helper lazily; if it's missing the inline fallback below kicks in.
    ced_text_result = ced_text_text(script_a or "", script_b or "")
    if ced_declared_result is not None:
        primary = "ced_declared"
        primary_value = ced_declared_result["normalized"]
        primary_raw = ced_declared_result["raw"]
    else:
        primary = "ced_text"
        primary_value = ced_text_result["ced_text_normalized"]
        primary_raw = ced_text_result["ced_text_raw"]
    return {
        "parsed": parseable,
        "parse_coverage": float(parseable),  # 0 or 1
        "ced_declared": ced_declared_result,
        "ced_text": ced_text_result,
        "primary_metric": primary,
        "primary_value": primary_value,
        "primary_raw": primary_raw,
    }


def ced_text_text(s_a: str, s_b: str) -> dict:
    """CED_text on raw script text (Levenshtein / length-normalised)."""
    import re
    a = re.sub(r"\s+", " ", s_a or "").strip()
    b = re.sub(r"\s+", " ", s_b or "").strip()
    if not a and not b:
        return {"ced_text_normalized": 0.0, "ced_text_raw": 0}
    if not a or not b:
        return {"ced_text_normalized": 1.0, "ced_text_raw": max(len(a), len(b))}
    raw = _levenshtein(a, b)
    return {"ced_text_normalized": raw / max(len(a), len(b)), "ced_text_raw": raw}


def compute_all(ir_a, ir_b, *,
                  declared_a=None, declared_b=None,
                  executed_a=None, executed_b=None) -> dict:
    """Compute all three CED metrics + pick the primary.

    Returns dict with keys: ced_text, ced_declared, ced_executed,
    primary_metric, primary_value, primary_raw.
    """
    text_result = ced_text(ir_a, ir_b)
    declared_result = ced_declared(ir_a, ir_b) if not text_result["normalized"] >= 0.0 else ced_declared(ir_a, ir_b)
    executed_result = None
    if executed_a is not None and executed_b is not None:
        executed_result = ced_executed(executed_a, executed_b)

    # Pick primary per spec §6.6.
    if declared_result.get("available"):
        primary = "CED_declared"
        primary_value = declared_result["normalized"]
        primary_raw = declared_result["raw"]
    elif text_result is not None:
        primary = "CED_text"
        primary_value = text_result["normalized"]
        primary_raw = text_result["raw"]
    else:
        primary = "unknown"
        primary_value = None
        primary_raw = None

    return {
        "ced_text": text_result,
        "ced_declared": declared_result,
        "ced_executed": executed_result,
        "primary_metric": primary,
        "primary_value": primary_value,
        "primary_raw": primary_raw,
    }


def compute_repair_cost(ced_values: list[dict | float],
                          *,
                          execution_attempts: int = 0,
                          verification_calls: int = 0,
                          lambda_exec: float = 0.1,
                          lambda_verify: float = 0.1) -> float:
    """RepairCost = Σ CED_declared(IR_t, IR_t+1) + λ_exec × #exec + λ_verify × #verify

    ced_values: list of CED_declared `raw` values OR dicts with 'raw' key
    """
    total = 0.0
    for v in ced_values:
        raw = v["raw"] if isinstance(v, dict) else v
        total += raw
    total += lambda_exec * execution_attempts
    total += lambda_verify * verification_calls
    return total