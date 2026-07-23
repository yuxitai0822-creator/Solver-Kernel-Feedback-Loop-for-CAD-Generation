"""Phase 2A Task A2.4 — validate code2oper parse coverage on clean
reconstruction-engine scripts (deterministic, well-formed) and report
per-script CED_declared if both are parseable.

Run:
    python experiments/phase2a_parse_coverage.py
Output:
    experiments/phase2a_parse_coverage.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code2oper"))
sys.path.insert(0, str(ROOT / "cad_edit_distance"))

from code2oper import parse_cadquery_script
from cad_edit_distance.compute_ced import ced_with_fallback

CLEAN = ROOT / "Reconstruction_results"
OUT = ROOT / "experiments" / "phase2a_parse_coverage"
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = OUT / "parse_coverage.json"


def main():
    sids = sorted([s for s in os.listdir(CLEAN)
                    if not s.endswith(".json") and s != "frozen_v0.1"])
    print(f"Found {len(sids)} samples")
    results = []
    n_parsed = 0
    n_total = 0
    n_ced_declared = 0
    n_ced_text = 0
    for sid in sids:
        path = CLEAN / sid / "generated_code.py"
        if not path.exists():
            continue
        n_total += 1
        script = path.read_text(encoding="utf-8")
        ops = parse_cadquery_script(script)
        parsed = ops is not None
        if parsed:
            n_parsed += 1
        # Compute CED for a synthetic pair (script vs itself, plus vs
        # next sample) to exercise ced_declared on parseable pairs.
        primary_metric = None
        primary_value = None
        try:
            res = ced_with_fallback(ops, ops, script, script)
            primary_metric = res["primary_metric"]
            primary_value = res["primary_value"]
            if primary_metric == "ced_declared":
                n_ced_declared += 1
            else:
                n_ced_text += 1
        except Exception as e:
            primary_metric = "error"
            primary_value = None
        n_ops = len(ops) if parsed else 0
        op_kinds = [op.operation for op in (ops or [])]
        results.append({
            "sample_id": sid,
            "parsed": parsed,
            "n_operations": n_ops,
            "op_kinds": op_kinds,
            "primary_metric": primary_metric,
            "primary_value": primary_value,
        })
    coverage = n_parsed / n_total if n_total else 0.0
    summary = {
        "n_total": n_total,
        "n_parsed": n_parsed,
        "parse_coverage": coverage,
        "n_ced_declared": n_ced_declared,
        "n_ced_text": n_ced_text,
        "results": results,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\nWrote {SUMMARY}")
    print(f"  Total scripts: {n_total}")
    print(f"  Parsed:        {n_parsed} ({coverage*100:.1f}%)")
    print(f"  CED_declared pairs: {n_ced_declared}")
    print(f"  CED_text fallback: {n_ced_text}")


if __name__ == "__main__":
    main()
