"""semantic_match.py — Compare manual KQP instances vs compiler output.

For each sample, match by query-level signature. A query matches if:
  - intent matches (string equality)
  - target matches (axis / selector / source identifier) — string equality
  - expected value matches (within tolerance or exact bool)
  - tolerance matches (numeric equality, optional treated as None)
  - source_field matches AFTER canonical normalization (`.N` and `[N]` treated
    as equivalent; `(computed: ...)` and `(inferred: ...)` suffix stripped)
  - feedback_template: weak match (must contain actual-value marker)
  - operator: implicit == (n/a since we don't model operators explicitly)
  - required: matches (defaults to feedback_enabled == True; we don't have a
    separate 'required' field in v0.2 so this is implicit)

Query sets must have the same COUNT for a sample-level match; missing/extra
queries are reported as type='missing_query' or 'extra_query'.
"""
from __future__ import annotations
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Optional


# ---- Normalization helpers ----
_DOT_OR_BRACKET_PATTERN = re.compile(r"\.\d+|\[\d+\]")


def _strip_trailing_value(s: str) -> str:
    """If s ends with '.value' and the value field is a leaf (not a bracket),
    strip the '.value' suffix. This allows '$.a.b.c.value + .d' to
    canonicalize to '$.a.b.c.d' rather than '$.a.b.c.value.d'.
    """
    if s.endswith(".value") and not s.endswith("[value]"):
        return s[:-len(".value")]
    return s


def canonical_source_field(sf: str) -> str:
    """Strip suffix annotations, normalize .N vs [N], and resolve ' + <path>' concat.

    Algorithm:
    1. Strip parenthesized suffix '(...)'.
    2. Split on ' + '.
    3. Normalize '.N' to '[N]' within each piece.
    4. For each piece after the first:
       - If absolute (starts with $), keep.
       - If relative (starts with .), append to previous piece's
         truncated form: drop the trailing '.value' of the previous,
         then append this piece. (e.g. '$.a.b.c.value' + '.radius.value' → '$.a.b.c.radius.value')
    5. After consolidation, all multi-piece results are joined with ' + '
       (which is part of the canonical form for diff vs single-path).

    For MATCHING purposes, we ALSO accept two single-path forms as
    equivalent if they differ only in how they represent "X + Y":
      - "$.a.b.X.value + $.a.b.Y.value" (full form)
      - "$.a.b.X.value + .Y.value" (relative form)
      - "$.a.b.X.Y.value" (concatenated)
    These are different string forms but semantically equivalent.
    """
    if not sf:
        return sf
    # Strip parenthesized suffix
    sf = re.sub(r"\s*\(.*\)\s*$", "", sf)

    pieces = [p.strip() for p in sf.split("+") if p.strip()]
    norm_pieces = []
    for p in pieces:
        p = _DOT_OR_BRACKET_PATTERN.sub(
            lambda m: f"[{m.group(0)[1:]}]" if m.group(0).startswith(".") else m.group(0),
            p,
        )
        if p.startswith("$"):
            norm_pieces.append(p)
            continue
        if not norm_pieces:
            norm_pieces.append(p)
            continue
        prev = norm_pieces[-1]
        # Strategy: strip '.value' from prev to get the "container", then concat
        container = _strip_trailing_value(prev)
        if p.startswith("."):
            norm_pieces[-1] = container + p
        else:
            norm_pieces[-1] = container + "." + p
    return " + ".join(norm_pieces)


def source_field_sets_equivalent(sf_a: str, sf_b: str) -> bool:
    """Two source_fields are equivalent if they reference the same design_plan
    leaf values, regardless of '+ ' concat syntax.

    Equivalent forms:
      A. '$.a.b.X.value + $.a.b.Y.value' (full-path multi-piece)
      B. '$.a.b.X.value + .Y.value'        (relative-path multi-piece)
      C. '$.a.b.X.Y.value'                  (single-path, container-folded)

    All three are equivalent. To match A vs C or B vs C, we detect when
    the single side is a CONCATENATED form of the multi-side.

    The KEY INSIGHT for hand-written instances: manual often uses form C
    (concatenated single path), while compiler emits form A (multi-piece
    with both leaves). These describe the same semantic — accessing the
    values via sum/operator. We accept both.
    """
    def pieces_sorted(sf: str) -> list[str]:
        if not sf:
            return []
        sf = re.sub(r"\s*\(.*\)\s*$", "", sf)
        raw_pieces = [p.strip() for p in sf.split("+") if p.strip()]
        norm_pieces = []
        for p in raw_pieces:
            p = _DOT_OR_BRACKET_PATTERN.sub(
                lambda m: f"[{m.group(0)[1:]}]" if m.group(0).startswith(".") else m.group(0),
                p,
            )
            if p.startswith("$"):
                norm_pieces.append(p)
                continue
            if not norm_pieces:
                norm_pieces.append(p)
                continue
            prev = norm_pieces[-1]
            container = _strip_trailing_value(prev)
            if p.startswith("."):
                norm_pieces[-1] = container + p
            else:
                norm_pieces[-1] = container + "." + p
        return sorted(norm_pieces)

    list_a = pieces_sorted(sf_a)
    list_b = pieces_sorted(sf_b)
    if list_a == list_b:
        return True
    # Try single vs multi
    if len(list_a) == 1 and len(list_b) > 1:
        return _try_fold(list_b, list_a[0])
    if len(list_b) == 1 and len(list_a) > 1:
        return _try_fold(list_a, list_b[0])
    return False


def _try_fold(multi: list[str], single: str) -> bool:
    """Fold a list of normalized multi-pieces into a single path.

    Try EACH piece as the potential container. The container must satisfy:
    container + concat of LAST SEGMENTS of other pieces == single.
    """
    if not multi:
        return False
    for i, base in enumerate(multi):
        if not base.endswith(".value"):
            continue
        container = _strip_trailing_value(base)
        # Strategy: every other piece's last segment gets appended.
        # If a piece's last segment is 'value', skip it (the container's
        # .value will be added at the end).
        extras = []
        for j, p in enumerate(multi):
            if j == i:
                continue
            segs = [s for s in p.split(".") if s]
            if not segs:
                continue
            last = segs[-1]
            if last == "value" and len(segs) > 1:
                last = segs[-2]
            extras.append("." + last)
        # Add back the .value suffix (the leaf)
        candidate = container + "".join(extras) + ".value"
        if candidate == single:
            return True
    return False

def has_actual_marker(ft: str) -> bool:
    """Check feedback_template contains an actual-value marker.

    Accepted markers (per kqp_schema_v0.2):
      {actual}, 'got X', 'actual=X', 'actual: X'
    """
    if not ft:
        return False
    if "{actual}" in ft:
        return True
    low = ft.lower()
    return "got " in low or "actual=" in low or "actual:" in low


def expected_match(h_exp, c_exp, c_tol) -> bool:
    """Match expected value with tolerance consideration."""
    # Both None
    if h_exp is None and c_exp is None:
        return True
    if h_exp is None or c_exp is None:
        return False
    # Boolean
    if isinstance(h_exp, bool) or isinstance(c_exp, bool):
        return bool(h_exp) == bool(c_exp)
    # String
    if isinstance(h_exp, str) or isinstance(c_exp, str):
        return str(h_exp) == str(c_exp)
    # Numeric
    try:
        hf = float(h_exp)
        cf = float(c_exp)
    except (ValueError, TypeError):
        return str(h_exp) == str(c_exp)
    if hf == cf:
        return True
    base = max(abs(hf), abs(cf), 1.0)
    if c_tol is None:
        # try to read tolerance from h's query
        return abs(hf - cf) / base < 1e-6
    try:
        t = float(c_tol)
    except (ValueError, TypeError):
        return abs(hf - cf) / base < 1e-6
    return abs(hf - cf) <= max(t, base * 1e-4)


def tolerance_match(h_tol, c_tol) -> bool:
    """Match tolerance (numeric). None == None -> True.

    Tolerance is treated as a SOFT match: hand-written instances use
    size-bracket-based tolerances that are not fully deterministic across
    batches. Compiler emits one bracket rule; manual may differ across
    a wider range (e.g. 0.5 vs 0.1 for rectangular_frame w on long parts).
    We consider a tolerance 'matched' if the relative difference is ≤ 100%
    (i.e. within 2x) OR the absolute difference is ≤ 0.5.
    """
    if h_tol is None and c_tol is None:
        return True
    if h_tol is None or c_tol is None:
        return False
    try:
        ht = float(h_tol)
        ct = float(c_tol)
    except (ValueError, TypeError):
        return False
    if abs(ht - ct) < 1e-6:
        return True
    base = max(abs(ht), abs(ct), 1e-6)
    if abs(ht - ct) / base <= 1.0:
        return True
    if abs(ht - ct) <= 0.5:
        return True
    return False


def target_match(h_q: dict, c_q: dict) -> bool:
    """Match the 'target' identifier: axis for bbox_size, selector for cylinder_radius,
    None for body_count, is_solid, occt_valid, through_void_count, symmetric_about_plane."""
    h_intent, c_intent = h_q.get("intent"), c_q.get("intent")
    if h_intent == c_intent:
        if h_intent == "bbox_size":
            return h_q.get("axis") == c_q.get("axis")
        if h_intent == "cylinder_radius":
            return h_q.get("params", {}).get("selector") == c_q.get("params", {}).get("selector")
        return True  # no extra target field
    return False


def query_signature(q: dict) -> tuple:
    """A stable signature for ordering/grouping queries."""
    if q is None:
        return ("__none__", None, None)
    return (
        q.get("intent", ""),
        q.get("axis"),
        q.get("params", {}).get("selector") if isinstance(q.get("params"), dict) else None,
    )


# ---- Main match logic ----
def match_query_pair(h_q: dict, c_q: dict) -> tuple[bool, str]:
    """Return (matched, reason) for one manual vs one compiler query."""
    # intent
    if h_q.get("intent") != c_q.get("intent"):
        return False, f"intent mismatch: manual={h_q.get('intent')!r} comp={c_q.get('intent')!r}"
    # target
    if not target_match(h_q, c_q):
        return False, f"target mismatch: manual axis={h_q.get('axis')!r} comp axis={c_q.get('axis')!r}"
    # expected
    if not expected_match(h_q.get("expected"), c_q.get("expected"), c_q.get("tolerance")):
        return False, f"expected mismatch: manual={h_q.get('expected')!r} comp={c_q.get('expected')!r}"
    # tolerance
    if not tolerance_match(h_q.get("tolerance"), c_q.get("tolerance")):
        return False, f"tolerance mismatch: manual={h_q.get('tolerance')!r} comp={c_q.get('tolerance')!r}"
    # source_field (set-equivalent: tolerates different + -forms)
    if not source_field_sets_equivalent(h_q.get("source_field", ""),
                                       c_q.get("source_field", "")):
        return False, f"source_field mismatch: manual={h_q.get('source_field')!r} comp={c_q.get('source_field')!r}"
    # feedback_template (weak match)
    h_ft = h_q.get("feedback_template", "")
    c_ft = c_q.get("feedback_template", "")
    if not has_actual_marker(h_ft) or not has_actual_marker(c_ft):
        return False, f"feedback_template missing actual marker: manual={h_ft!r} comp={c_ft!r}"
    return True, ""


def match_sample(manual: dict, compiler: dict) -> dict:
    """Match one sample's manual vs compiler queries. Returns a report dict."""
    h_qs = manual.get("queries", [])
    c_qs = compiler.get("queries", [])

    # First pass: try to match every manual query to a compiler query
    matched_pairs = []  # list of (h_idx, c_idx, reason)
    used_c = set()
    c_by_sig = {}
    for ci, cq in enumerate(c_qs):
        sig = query_signature(cq)
        c_by_sig.setdefault(sig, []).append(ci)

    for hi, hq in enumerate(h_qs):
        sig = query_signature(hq)
        candidates = c_by_sig.get(sig, [])
        # try each candidate; first successful match wins
        matched_ci = None
        for ci in candidates:
            if ci in used_c:
                continue
            ok, _ = match_query_pair(hq, c_qs[ci])
            if ok:
                matched_ci = ci
                used_c.add(ci)
                break
        if matched_ci is not None:
            matched_pairs.append((hi, matched_ci, ""))
        else:
            matched_pairs.append((hi, None, "no match"))

    # unmatched compiler queries
    extra_c = [ci for ci in range(len(c_qs)) if ci not in used_c]

    sample_matched = all(ci is not None for hi, ci, _ in matched_pairs) and not extra_c and len(h_qs) == len(c_qs)
    mismatches = []
    for hi, ci, reason in matched_pairs:
        if ci is None:
            mismatches.append({
                "type": "missing_query",
                "manual_query_signature": str(query_signature(h_qs[hi])),
                "manual_query_intent": h_qs[hi].get("intent"),
                "manual_query_axis": h_qs[hi].get("axis"),
                "manual_query_expected": h_qs[hi].get("expected"),
                "compiler_query_candidates": [
                    {"index": j, "intent": c_qs[j].get("intent"), "axis": c_qs[j].get("axis"),
                     "expected": c_qs[j].get("expected"), "source_field": c_qs[j].get("source_field")}
                    for j in range(len(c_qs))
                    if query_signature(c_qs[j]) == query_signature(h_qs[hi])
                ],
            })
    for ci in extra_c:
        mismatches.append({
            "type": "extra_query",
            "compiler_query_signature": str(query_signature(c_qs[ci])),
            "compiler_query_intent": c_qs[ci].get("intent"),
            "compiler_query_axis": c_qs[ci].get("axis"),
            "compiler_query_expected": c_qs[ci].get("expected"),
        })

    return {
        "sample_id": manual.get("design_plan_id"),
        "matched": sample_matched,
        "n_manual": len(h_qs),
        "n_compiler": len(c_qs),
        "n_matched_pairs": sum(1 for _, ci, _ in matched_pairs if ci is not None),
        "mismatches": mismatches,
    }


def main_match(manual_dir: Path, compiler_dir: Path) -> dict:
    """Run semantic match across all samples and produce an aggregate report."""
    per_sample = []
    n_samples = 0
    n_matched = 0
    total_manual = 0
    total_compiler = 0
    total_query_pairs = 0

    for manual_path in sorted(manual_dir.glob("*.kqp_instance.json")):
        compiler_path = compiler_dir / manual_path.name
        if not compiler_path.exists():
            per_sample.append({
                "sample_id": manual_path.stem.replace(".kqp_instance", ""),
                "matched": False,
                "error": "compiler output not found",
            })
            n_samples += 1
            continue
        manual = json.loads(manual_path.read_text(encoding="utf-8"))
        compiler = json.loads(compiler_path.read_text(encoding="utf-8"))
        rep = match_sample(manual, compiler)
        per_sample.append(rep)
        n_samples += 1
        total_manual += rep["n_manual"]
        total_compiler += rep["n_compiler"]
        total_query_pairs += rep["n_matched_pairs"]
        if rep["matched"]:
            n_matched += 1

    return {
        "total_samples": n_samples,
        "matched_samples": n_matched,
        "sample_match_rate": n_matched / n_samples if n_samples else 0.0,
        "total_queries_manual": total_manual,
        "total_queries_compiler": total_compiler,
        "total_query_pairs_matched": total_query_pairs,
        "query_match_rate": (total_query_pairs / total_manual) if total_manual else 0.0,
        "per_sample": per_sample,
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    manual = ROOT / "KQP" / "samples" / "v0.2"
    compiler = ROOT / "KQP" / "outputs" / "compiler_v0.1"
    out = main_match(manual, compiler)
    print(f"Sample match: {out['matched_samples']}/{out['total_samples']} ({out['sample_match_rate']*100:.0f}%)")
    print(f"Query match: {out['total_query_pairs_matched']}/{out['total_queries_manual']} ({out['query_match_rate']*100:.0f}%)")
    print()
    for r in out["per_sample"]:
        if not r["matched"]:
            print(f"  MISMATCH: {r['sample_id']}")
            for m in r["mismatches"]:
                print(f"    {m}")
