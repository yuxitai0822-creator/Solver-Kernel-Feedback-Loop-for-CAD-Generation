"""Phase 2B Final Analysis — McNemar per layer, per-(method, layer) failure rates.

Reads:
  - experiments/phase2b_full/pilot_results.json (raw trial results)
  - experiments/phase2b_full/kqp_rerun.json   (KQP bbox re-eval)

Computes:
  - Per-(method, layer) step-export rate and KQP-failure rate
  - McNemar exact p-value for M0 vs M2 on each layer
  - Per-layer per-operator breakdown

Writes:
  - experiments/phase2b_full/final_summary.json
  - experiments/phase2b_full/final_report.md
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "experiments" / "phase2b_full"
RESULTS_PATH = OUT_DIR / "pilot_results.json"
KQP_PATH = OUT_DIR / "kqp_rerun.json"
SUMMARY_PATH = OUT_DIR / "final_summary.json"
REPORT_PATH = OUT_DIR / "final_report.md"


def mcnemar_exact_p(b, c):
    """Exact two-sided McNemar p-value for a 2x2 discordant-count table.

    b = #cases M0 pass & M2 fail, c = #cases M0 fail & M2 pass.
    Returns the two-sided binomial p-value under H0: P(b)=P(c).
    """
    n = b + c
    if n == 0:
        return 1.0
    # Two-sided p = 2 * min(P(X <= b), P(X >= b)) for X ~ Bin(n, 0.5)
    # with continuity-style handling near 0 / n.
    from math import comb
    def binom_pmf(k, n):
        return comb(n, k) / (2 ** n)
    p_le = sum(binom_pmf(k, n) for k in range(0, b + 1))
    p_ge = sum(binom_pmf(k, n) for k in range(b, n + 1))
    p_one_sided = min(p_le, p_ge)
    return min(1.0, 2 * p_one_sided)


def main():
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    kqp_results = json.loads(KQP_PATH.read_text(encoding="utf-8")) if KQP_PATH.exists() else []

    # Filter: drop the 552 old errored entries (DEEPSEEK key bug).
    # Keep only the freshly-run real trials.
    real = [r for r in results if "error" not in r]
    print(f"Total results: {len(results)}  (real: {len(real)}  errored: {len(results)-len(real)})")

    # Build KQP lookup
    kqp_by_key = {(r["method"], r["sid"], r["nid"]): r.get("kqp_rerun", {})
                  for r in kqp_results}

    # Per-(method, layer) tallies
    by_ml = defaultdict(lambda: {
        "n_total": 0,
        "n_step_export": 0,
        "n_step_export_occt_load": 0,
        "n_kqp_run": 0,
        "n_kqp_fail": 0,
    })
    for r in real:
        key = (r["method"], r["layer"])
        by_ml[key]["n_total"] += 1
        if r.get("step_export"):
            by_ml[key]["n_step_export"] += 1
        if r.get("occt_load"):
            by_ml[key]["n_step_export_occt_load"] += 1
        kr = kqp_by_key.get((r["method"], r["sid"], r["nid"]))
        if kr and "n_bbox_queries" in kr:
            by_ml[key]["n_kqp_run"] += 1
            if kr.get("n_bbox_fail", 0) > 0:
                by_ml[key]["n_kqp_fail"] += 1

    # Per-operator (E1, E2, E3, EX2) tallies within each (method, layer)
    by_op = defaultdict(lambda: defaultdict(int))  # (op, method) -> count
    for r in real:
        op = r.get("operator", "?")
        by_op[(op, r["method"])]["n_total"] += 1
        if r.get("step_export"):
            by_op[(op, r["method"])]["n_step_export"] += 1
        kr = kqp_by_key.get((r["method"], r["sid"], r["nid"]))
        if kr and kr.get("n_bbox_fail", 0) > 0:
            by_op[(op, r["method"])]["n_kqp_fail"] = by_op[(op, r["method"])].get("n_kqp_fail", 0) + 1

    # McNemar: per layer, M0 vs M2 KQP-fail concordance
    mcnemar_by_layer = {}
    for layer in ("TypeA", "EX2"):
        m0_keys = {(r["sid"], r["nid"]) for r in real
                    if r["method"] == "M0_NoFeedback" and r["layer"] == layer}
        m2_keys = {(r["sid"], r["nid"]) for r in real
                    if r["method"] == "M2_KQPOnly" and r["layer"] == layer}
        common = m0_keys & m2_keys
        b = c = 0
        for sid, nid in common:
            m0_fail = kqp_by_key.get(("M0_NoFeedback", sid, nid), {}).get("n_bbox_fail", 0) > 0
            m2_fail = kqp_by_key.get(("M2_KQPOnly", sid, nid), {}).get("n_bbox_fail", 0) > 0
            if not m0_fail and m2_fail:
                b += 1
            elif m0_fail and not m2_fail:
                c += 1
        p = mcnemar_exact_p(b, c)
        mcnemar_by_layer[layer] = {"b_M0pass_M2fail": b, "c_M0fail_M2pass": c, "p": p}

    # McNemar: M0 vs M3 (combined solver+KQP)
    mcnemar03_by_layer = {}
    for layer in ("TypeA", "EX2"):
        m0_keys = {(r["sid"], r["nid"]) for r in real
                    if r["method"] == "M0_NoFeedback" and r["layer"] == layer}
        m3_keys = {(r["sid"], r["nid"]) for r in real
                    if r["method"] == "M3_SolverKQP" and r["layer"] == layer}
        common = m0_keys & m3_keys
        b = c = 0
        for sid, nid in common:
            m0_fail = kqp_by_key.get(("M0_NoFeedback", sid, nid), {}).get("n_bbox_fail", 0) > 0
            m3_fail = kqp_by_key.get(("M3_SolverKQP", sid, nid), {}).get("n_bbox_fail", 0) > 0
            if not m0_fail and m3_fail:
                b += 1
            elif m0_fail and not m3_fail:
                c += 1
        p = mcnemar_exact_p(b, c)
        mcnemar03_by_layer[layer] = {"b_M0pass_M3fail": b, "c_M0fail_M3pass": c, "p": p}

    # Write JSON summary
    summary = {
        "n_total_results": len(results),
        "n_real": len(real),
        "n_errored": len(results) - len(real),
        "by_method_layer": {f"{m}|{l}": v for (m, l), v in sorted(by_ml.items())},
        "mcnemar_M0_vs_M2": mcnemar_by_layer,
        "mcnemar_M0_vs_M3": mcnemar03_by_layer,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write markdown report
    lines = []
    lines.append("# Phase 2B Full Benchmark — Final Report")
    lines.append("")
    lines.append(f"**Total trials in file**: {len(results)}  ")
    lines.append(f"- real: {len(real)}")
    lines.append(f"- errored (auth / network / OCP): {len(results) - len(real)}")
    lines.append("")
    lines.append("## Headline — per (method, layer)")
    lines.append("")
    lines.append("| Method | Layer | n | step_export | occt_load | KQP run | KQP fail | rate |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for (m, l), v in sorted(by_ml.items()):
        n = v["n_total"]
        se = v["n_step_export"]
        oc = v["n_step_export_occt_load"]
        kr = v["n_kqp_run"]
        kf = v["n_kqp_fail"]
        rate = f"{kf/kr*100:.1f}%" if kr > 0 else "—"
        lines.append(f"| {m} | {l} | {n} | {se} | {oc} | {kr} | {kf} | {rate} |")
    lines.append("")
    lines.append("## McNemar — M0 vs M2")
    lines.append("")
    lines.append("| Layer | b (M0 pass, M2 fail) | c (M0 fail, M2 pass) | p (exact, two-sided) | direction |")
    lines.append("|---|---:|---:|---:|---|")
    for layer, mc in mcnemar_by_layer.items():
        b, c, p = mc["b_M0pass_M2fail"], mc["c_M0fail_M2pass"], mc["p"]
        if b == 0 and c == 0:
            direction = "no discordant pairs"
        elif c > b:
            direction = f"M2 better (M0 fail-M2 pass by {c-b})"
        else:
            direction = f"M0 better (M2 fail-M0 pass by {b-c})"
        lines.append(f"| {layer} | {b} | {c} | {p:.4f} | {direction} |")
    lines.append("")
    lines.append("## McNemar — M0 vs M3")
    lines.append("")
    lines.append("| Layer | b (M0 pass, M3 fail) | c (M0 fail, M3 pass) | p (exact, two-sided) | direction |")
    lines.append("|---|---:|---:|---:|---|")
    for layer, mc in mcnemar03_by_layer.items():
        b, c, p = mc["b_M0pass_M3fail"], mc["c_M0fail_M3pass"], mc["p"]
        if b == 0 and c == 0:
            direction = "no discordant pairs"
        elif c > b:
            direction = f"M3 better (M0 fail-M3 pass by {c-b})"
        else:
            direction = f"M0 better (M3 fail-M0 pass by {b-c})"
        lines.append(f"| {layer} | {b} | {c} | {p:.4f} | {direction} |")
    lines.append("")
    lines.append("## Per-operator — step_export rate")
    lines.append("")
    ops = sorted(set(op for (op, m) in by_op.keys()))
    methods = sorted(set(m for (op, m) in by_op.keys()))
    header = "| operator | " + " | ".join(methods) + " |"
    sep = "|---|" + "---|" * len(methods)
    lines.append(header)
    lines.append(sep)
    for op in ops:
        cells = [op]
        for m in methods:
            d = by_op.get((op, m), {})
            n = d.get("n_total", 0)
            se = d.get("n_step_export", 0)
            cells.append(f"{se}/{n}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
