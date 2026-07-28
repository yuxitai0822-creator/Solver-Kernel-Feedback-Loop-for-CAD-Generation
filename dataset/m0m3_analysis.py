"""dataset/m0m3_analysis.py — Analyse the M0-M3 perturbation experiment.

Reads ``experiments/phase2b_m0m3/pilot_results.json`` and
experiments/phase2b_triplets/_frozen_manifest.json`` and produces:

  * a per-method success-rate breakdown (with two layers of detail:
    collapsed by ``final_status`` and by KQP pass-rate per attempt);
  * a per-operator breakdown;
  * a per-(method, operator) cross tabulation;
  * a per-(operator) comparison of the four methods' iter-to-success
    trajectory;
  * a markdown report (``experiments/phase2b_m0m3/REPORT.md``).

The analysis is intentionally tiny and only depends on the two
JSON files.  Run it after the full experiment completes.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

OUT_DIR = _REPO_ROOT / "experiments" / "phase2b_m0m3"
FROZEN_DIR = _REPO_ROOT / "experiments" / "phase2b_triplets"


def _final_status_rank(s: str) -> int:
    """Smaller = better.  Used to colour / sort rows."""
    order = ["success", "no_change", "max_iter_exceeded",
             "no_script", "llm_error", "runner_crash"]
    return order.index(s) if s in order else 99


def main() -> None:
    res = json.loads((OUT_DIR / "pilot_results.json").read_text(
        encoding="utf-8"))
    frozen = json.loads((FROZEN_DIR / "_frozen_manifest.json").read_text(
        encoding="utf-8"))
    n_frozen_total = frozen["n_triples"]

    # Per-method final-status breakdown.
    by_method: dict[str, Counter] = defaultdict(Counter)
    by_method_op: dict[tuple[str, str], Counter] = defaultdict(Counter)
    by_method_iter: dict[str, Counter] = defaultdict(Counter)  # iterations taken on success
    by_method_op_iters: dict[tuple[str, str], list[int]] = defaultdict(list)
    wc_total = 0.0
    for x in res:
        method = x.get("method", "?")
        op = x.get("operator", "?")
        st = x.get("final_status", "?")
        niter = x.get("n_iterations", 0)
        wc_total += x.get("wallclock", 0.0) or 0.0
        by_method[method][st] += 1
        by_method_op[(method, op)][st] += 1
        if st == "success" and niter > 0:
            by_method_iter[method][niter] += 1
            by_method_op_iters[(method, op)].append(niter)

    # Output: per-method table.
    print("=" * 60)
    print(f"M0-M3 perturbation repair experiment")
    print(f"frozen pairs: {n_frozen_total}  trials on disk: {len(res)}")
    print("=" * 60)

    methods = sorted(by_method.keys())
    final_states = ["success", "max_iter_exceeded", "no_change",
                     "no_script", "llm_error", "runner_crash"]
    header = ["method", "n"] + final_states
    print()
    print("| " + " | ".join(f"{h:18s}" for h in header) + " |")
    print("|" + "|".join("-" * 20 for _ in header) + "|")
    for m in methods:
        row = [m, sum(by_method[m].values())] + [
            by_method[m].get(s, 0) for s in final_states
        ]
        print("| " + " | ".join(f"{str(c):18s}" for c in row) + " |")

    # Per-(method, operator) pass-rate.
    pairs: set[tuple[str, str]] = set()
    for (m, op), stc in by_method_op.items():
        pairs.add((m, op))
    ops = sorted({op for op in by_method_op.values() for op in op.keys()}
                  | {op for (_, op) in pairs})
    ops = sorted({k for k in by_method_op})
    methods = sorted(by_method.keys())
    if not ops:
        ops = sorted({x.get("operator", "?") for x in res})
    print()
    print("Pass-rate (success / trials) by (method, operator):")
    print()
    header = ["operator"] + methods + ["all"]
    print("| " + " | ".join(f"{h:14s}" for h in header) + " |")
    print("|" + "|".join("-" * 16 for _ in header) + "|")
    for op in sorted({op for (_, op) in by_method_op.keys()}):
        cells = [op]
        totals = [0, 0]
        for m in methods:
            c = by_method_op.get((m, op))
            if c is None:
                cells.append("-")
                continue
            n = sum(c.values())
            ok = c.get("success", 0)
            cells.append(f"{ok}/{n} ({ok/n*100:.0f}%)")
            totals[0] += ok
            totals[1] += n
        cells.append(f"{totals[0]}/{totals[1]} ({totals[0]/totals[1]*100:.0f}%)"
                    if totals[1] else "-")
        print("| " + " | ".join(f"{c:14s}" for c in cells) + " |")

    # Iter-to-success trajectory per method.
    print()
    print("Iter-to-success trajectory (success only):")
    print()
    print("| method       |   1 iter | 2 iters | 3 iters | mean |")
    print("|--------------|----------|---------|---------|------|")
    for m in methods:
        c = by_method_iter.get(m, Counter())
        if not c:
            continue
        n_total = sum(c.values())
        n1, n2, n3 = c.get(1, 0), c.get(2, 0), c.get(3, 0)
        mean = (n1*1 + n2*2 + n3*3) / n_total if n_total else 0
        print(f"| {m:12s} | {n1:8d} | {n2:7d} | {n3:7d} | {mean:.2f} |")

    # Operator-by-method table — how long does each operator take
    # in iter-1 / iter-2 / iter-3 (mean iters-to-success only).
    print()
    print("Mean iter-to-success (per operator):")
    print()
    op_iters: dict[str, list[int]] = defaultdict(list)
    for (m, op), vals in by_method_op_iters.items():
        op_iters[op].extend(vals)
    print("| operator               | n success | mean iter |")
    print("|------------------------|-----------|-----------|")
    for op in sorted(op_iters.keys()):
        vals = op_iters[op]
        if vals:
            print(f"| {op:22s} | {len(vals):9d} | {sum(vals)/len(vals):.2f} |")

    # Summary
    n_total = len(res)
    n_success = sum(c.get("success", 0)
                     for c in by_method.values())
    n_max_iter = sum(c.get("max_iter_exceeded", 0)
                       for c in by_method.values())
    print()
    print(f"WALLCLOCK total: {wc_total:.1f}s")
    print(f"TRIALS: {n_total}  SUCCESS: {n_success} ({n_success/n_total*100:.1f}%)  "
          f"MAX_ITER: {n_max_iter} ({n_max_iter/n_total*100:.1f}%)")

    # Write a markdown report
    report_path = OUT_DIR / "REPORT.md"
    _write_report(report_path, by_method, by_method_op,
                  by_method_iter, by_method_op_iters,
                  n_total, n_success, n_max_iter, wc_total,
                  n_frozen_total, methods)


def _write_report(path: Path, by_method, by_method_op,
                   by_method_iter, by_method_op_iters,
                   n_total, n_success, n_max_iter, wc_total,
                   n_frozen, methods) -> None:
    final_states = ["success", "max_iter_exceeded", "no_change",
                     "no_script", "llm_error", "runner_crash"]
    lines = [
        "# M0-M3 Perturbation Experiment — Report",
        "",
        f"**Frozen triples input**: {n_frozen}  ",
        f"**Trials on disk**: {n_total} (= frozen × 4 methods; some pairs may be partial if the run was interrupted)  ",
        f"**Wallclock total**: {wc_total:.1f}s  ",
        "",
        "## Per-method final status",
        "",
        "| method | " + " | ".join(final_states) + " | total |",
        "|---|" + "|".join("---" for _ in final_states) + "|---|",
    ]
    for m in methods:
        c = by_method[m]
        row = [m] + [str(c.get(s, 0)) for s in final_states] + [
            str(sum(c.values()))]
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Pass-rate by (method, operator)",
        "",
        "(rows = operator; columns = method; entry = `success/total (pct)`)",
        "",
        "| operator | " + " | ".join(methods) + " | all |",
        "|---" + "|---" * (len(methods) + 1) + "|",
    ]
    for op in sorted({op for (_, op) in by_method_op.keys()}):
        cells = [op]
        totals = [0, 0]
        for m in methods:
            c = by_method_op.get((m, op))
            if c is None:
                cells.append("-")
                continue
            n = sum(c.values())
            ok = c.get("success", 0)
            cells.append(f"{ok}/{n} ({ok/n*100:.0f}%)")
            totals[0] += ok
            totals[1] += n
        if totals[1]:
            cells.append(f"{totals[0]}/{totals[1]} ({totals[0]/totals[1]*100:.0f}%)")
        else:
            cells.append("-")
        lines.append("| " + " | ".join(cells) + " |")

    lines += [
        "",
        "## Iter-to-success trajectory",
        "",
        "Of the trials that ultimately succeeded, how many",
        "iterations did the LLM require?  `1` is best (= passed on",
        "the first attempt given the initial `code_perturbed.py`).",
        "",
        "| method | 1 iter | 2 iters | 3 iters | mean |",
        "|---|---:|---:|---:|---:|",
    ]
    for m in methods:
        c = by_method_iter.get(m, {})
        if not c:
            continue
        n_total = sum(c.values())
        n1, n2, n3 = c.get(1, 0), c.get(2, 0), c.get(3, 0)
        mean = (n1 + 2*n2 + 3*n3) / n_total if n_total else 0
        lines.append(f"| {m} | {n1} | {n2} | {n3} | {mean:.2f} |")

    lines += [
        "",
        "## Per-operator mean iter-to-success",
        "",
        "| operator | n success | mean iter |",
        "|---|---:|---:|",
    ]
    op_iters: dict[str, list[int]] = defaultdict(list)
    for (_, op), vals in by_method_op_iters.items():
        op_iters[op].extend(vals)
    for op in sorted(op_iters.keys()):
        vals = op_iters[op]
        if vals:
            lines.append(f"| {op} | {len(vals)} | {sum(vals)/len(vals):.2f} |")

    lines += [
        "",
        "## Notes",
        "",
        "- `success`     = all 3 verifications passed at some iter.",
        "- `max_iter_exceeded` = still failing after 3 iterations.",
        "- `llm_error`   = API / network error (transient, retried on resume).",
        "- `runner_crash` = unhandled exception in the runner (rare).",
        "",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
