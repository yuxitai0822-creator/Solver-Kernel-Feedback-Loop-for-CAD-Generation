"""dataset/m0m3_significance.py — McNemar exact two-sided p-values
across the four methods (paired by (sid, nid) since the same 120
frozen triples go through all four methods).

Writes the result table to ``experiments/phase2b_m0m3/SIGNIFICANCE.md``.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from math import comb

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

OUT_DIR = _REPO_ROOT / "experiments" / "phase2b_m0m3"
METHODS = ["M0_NoFeedback", "M1_SolverOnly", "M2_KQPOnly", "M3_SolverKQP"]


def mcnemar_exact_p(b: int, c: int) -> float:
    """Two-sided McNemar exact p-value (binomial under H0: P=0.5)."""
    if b + c == 0:
        return 1.0
    n = b + c

    def binom_pmf(k, n):
        return comb(n, k) / (2 ** n)
    p_le = sum(binom_pmf(k, n) for k in range(0, b + 1))
    p_ge = sum(binom_pmf(k, n) for k in range(b, n + 1))
    return min(1.0, 2 * min(p_le, p_ge))


def _diff(by_pair, a: str, b: str) -> tuple[int, int]:
    """Return ``(a_wins, b_wins)`` for the pair of methods, where
    a "win" means that method passed while the other did not.
    Symmetric in (a, b) — caller can pass either order."""
    if a == b:
        return (0, 0)
    x_win = 0
    y_win = 0
    for k, results in by_pair.items():
        va = results.get(a, False)
        vb = results.get(b, False)
        if va and not vb:
            x_win += 1
        elif vb and not va:
            y_win += 1
    return (x_win, y_win)


def main() -> None:
    res = json.loads((OUT_DIR / "pilot_results.json").read_text(
                     encoding="utf-8"))

    # Build a per-(sid, nid) per-method pass index.
    by_pair: dict[tuple[str, str], dict[str, bool]] = {}
    for x in res:
        key = (x.get("sid"), x.get("nid"))
        m = x.get("method")
        by_pair.setdefault(key, {})[m] = (x.get("final_status") == "success")

    pairs = list(by_pair.keys())
    n_pairs = len(pairs)
    print(f"Pairs in common: {n_pairs}")

    # No precomputed discordant dict — _diff handles symmetric lookup.

    # Pass-rate per method
    pass_per_method: dict[str, int] = {m: 0 for m in METHODS}
    n = 0
    for x in res:
        if x.get("method") in pass_per_method:
            pass_per_method[x["method"]] += int(x.get("final_status") == "success")
            if n < 1 or all(pass_per_method.values()):
                n = max(n, len([k for k in res if k.get("method") == x["method"]]))

    # Pass-rate per method
    pass_per_method: dict[str, int] = {m: 0 for m in METHODS}
    n = 0
    for x in res:
        if x.get("method") in pass_per_method:
            pass_per_method[x["method"]] += int(x.get("final_status") == "success")
            if n < 1 or all(pass_per_method.values()):
                n = max(n, len([k for k in res if k.get("method") == x["method"]]))

    # Render markdown.
    lines = [
        "# M0-M3 Significance Analysis",
        "",
        "**Frozen triples input**: 120 (each tested under all four methods)  ",
        f"**Common (sid, nid) pairs**: {n_pairs}  ",
        "",
        "## Pass counts",
        "",
        "| method | pass / total | pass rate |",
        "|---|---:|---:|",
    ]
    for m in METHODS:
        c = pass_per_method[m]
        lines.append(f"| {m} | {c} / {n_pairs} | {c/n_pairs*100:.1f}% |")

    lines += [
        "",
        "## McNemar pairwise (paired on (sid, nid))",
        "",
        "Each cell = `a_wins / b_wins` followed by the exact two-sided",
        "McNemar p-value.  `a_wins` is the number of pairs in which the",
        "row method succeeded but the column method did not; `b_wins` is",
        "the reverse.",
        "",
        "| row \\\\ column | " + " | ".join(METHODS) + " |",
        "|---|" + "|".join("---" for _ in METHODS) + "|",
    ]
    for a in METHODS:
        cells = [a]
        for b in METHODS:
            if a == b:
                cells.append("—")
            else:
                aw, bw = _diff(by_pair, a, b)
                p = mcnemar_exact_p(aw, bw)
                sig = "*" if p < 0.05 else ""
                cells.append(f"{aw}/{bw} p={p:.4f}{sig}")
        lines.append("| " + " | ".join(cells) + " |")

    lines += [
        "",
        "(`*` = p < 0.05)",
        "",
        "## Interpretation",
        "",
    ]

    def headline(a: str, b: str, question: str) -> None:
        aw, bw = _diff(by_pair, a, b)
        p = mcnemar_exact_p(aw, bw)
        verdict = "**significant**" if p < 0.05 else "n.s."
        lines.append(
            f"**{a} vs {b}** — {a} wins in {aw}, {b} wins in {bw}; "
            f"McNemar p = {p:.4f}; {verdict}.  {question}"
        )

    headline("M0_NoFeedback", "M2_KQPOnly",
              "Does KQP feedback beat no feedback?")
    headline("M1_SolverOnly", "M2_KQPOnly",
              "Does KQP feedback beat solver-only feedback?")
    headline("M0_NoFeedback", "M1_SolverOnly",
              "Does solver feedback beat no feedback? (intuition: no)")
    headline("M2_KQPOnly", "M3_SolverKQP",
              "Does adding solver feedback to KQP feedback help?")
    headline("M3_SolverKQP", "M1_SolverOnly",
              "Combined vs solver-only — does adding KQP help?")

    lines += [
        "",
    ]

    out = OUT_DIR / "SIGNIFICANCE.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
