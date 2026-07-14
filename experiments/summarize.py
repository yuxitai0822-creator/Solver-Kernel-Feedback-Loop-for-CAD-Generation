"""summarize.py — Aggregate `run_result.json` files into per-method + master summaries.

Usage:
  python summarize.py
  python summarize.py --results-dir experiments/results --out-dir experiments/reports

Reads from: experiments/results/<method>/<sample_id>/run_result.json
Writes to:
  experiments/reports/benchmark_<method>_summary.json
  experiments/reports/benchmark_master_summary.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


METHOD_LABEL = {
    "no_feedback": "M0_NoFeedback",
    "solver_only": "M1_SolverOnly",
    "kqp_only": "M2_KQPOnly",
    "solver_kqp": "M3_SolverKQP",
}


def list_run_results(results_dir: Path) -> dict[str, list[dict]]:
    """Walk results_dir/<method>/*/run_result.json and group by method id."""
    by_method: dict[str, list[dict]] = defaultdict(list)
    if not results_dir.exists():
        return by_method
    for method_dir in results_dir.iterdir():
        if not method_dir.is_dir():
            continue
        for sample_dir in method_dir.iterdir():
            if not sample_dir.is_dir():
                continue
            rrf = sample_dir / "run_result.json"
            if not rrf.exists():
                continue
            try:
                rec = json.loads(rrf.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  ! could not parse {rrf}: {e}")
                continue
            # Method in run_result is the canonical "no_feedback" / "solver_only" etc.
            mid = rec.get("method", "unknown")
            by_method[mid].append(rec)
    return by_method


def _agg_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {}
    n_s1 = sum(1 for r in rows if r["metrics"]["success_at_1"])
    n_s2 = sum(1 for r in rows if r["metrics"]["success_at_2"])
    n_s3 = sum(1 for r in rows if r["metrics"]["success_at_3"])
    n_f2s = sum(1 for r in rows if r["metrics"]["failure_to_success"])
    iter_to_success = [r["final_status"]["iterations_used"]
                          for r in rows if r["final_status"]["success"]]
    return {
        "n_samples": n,
        "n_initial_pass": sum(1 for r in rows if r["initial_status"]["kqp_pass"]),
        "n_final_pass": sum(1 for r in rows if r["final_status"]["final_kqp_pass"]),
        "Success@1": n_s1 / n,
        "Success@2": n_s2 / n,
        "Success@3": n_s3 / n,
        "F2S_ConversionRate": n_f2s / n,
        "n_iterations_to_success_distribution": {
            "1": sum(1 for k in iter_to_success if k == 1),
            "2": sum(1 for k in iter_to_success if k == 2),
            "3": sum(1 for k in iter_to_success if k == 3),
        },
        "MeanIterationsToSuccess": (sum(iter_to_success) / len(iter_to_success)
                                       if iter_to_success else None),
        "MeanCED_declared_total": (sum(r["metrics"]["ced_declared_total"]
                                          for r in rows) / n if n else 0),
        "MeanCED_executed_total": (sum(r["metrics"]["ced_executed_total"]
                                          for r in rows) / n if n else 0),
        "MeanRepairCost": (sum(r["metrics"]["repair_cost"]
                                  for r in rows) / n if n else 0),
        "MeanRuntimeCost_s": (sum(r["metrics"]["runtime_sec"]
                                      for r in rows) / n if n else 0),
        "MeanInputTokens": (sum(r["metrics"]["input_tokens"]
                                   for r in rows) / n if n else 0),
        "MeanOutputTokens": (sum(r["metrics"]["output_tokens"]
                                    for r in rows) / n if n else 0),
        "MeanTotalTokens": (sum(r["metrics"]["total_tokens"]
                                   for r in rows) / n if n else 0),
        "n_failure_to_success": n_f2s,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="experiments/results",
                      help="directory containing <method>/<sample_id>/run_result.json")
    ap.add_argument("--out-dir", default="experiments/reports",
                      help="directory for output summaries")
    args = ap.parse_args()

    results_dir = ROOT / args.results_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    by_method = list_run_results(results_dir)
    if not by_method:
        print(f"No run_result.json files found under {results_dir}")
        return

    print(f"Found runs for {len(by_method)} method(s):")
    for mid, rows in by_method.items():
        print(f"  {mid} ({METHOD_LABEL.get(mid, '?')}): {len(rows)} runs")

    # Per-method summary
    summaries: dict[str, dict] = {}
    for mid, rows in by_method.items():
        agg = _agg_metrics(rows)
        report = {
            "method": mid,
            "method_label": METHOD_LABEL.get(mid, mid),
            "schema_version": "run_result_v0.1",
            "metrics": agg,
            "n_samples": len(rows),
            "rows": rows,
        }
        out_path = out_dir / f"benchmark_{mid}_summary.json"
        out_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8")
        summaries[mid] = agg
        print(f"  → {out_path.relative_to(ROOT)}: Success@3={agg['Success@3']:.2%}, "
              f"MeanRepairCost={agg['MeanRepairCost']:.2f}, "
              f"MeanTotalTokens={agg['MeanTotalTokens']:.0f}")

    # Master
    master = {
        "experiment": "Solver-KQP Repair Loop Benchmark v0.1",
        "schema_version": "run_result_v0.1",
        "methods": summaries,
        "comparison_table": {
            "M0_NoFeedback": summaries.get("no_feedback", {}),
            "M1_SolverOnly": summaries.get("solver_only", {}),
            "M2_KQPOnly": summaries.get("kqp_only", {}),
            "M3_SolverKQP": summaries.get("solver_kqp", {}),
        },
    }
    master_path = out_dir / "benchmark_master_summary.json"
    master_path.write_text(json.dumps(master, indent=2,
                                          ensure_ascii=False, default=str),
                              encoding="utf-8")
    print(f"\nMaster summary → {master_path.relative_to(ROOT)}")
    print("\n=== Comparison Table ===")
    print(f"{'Method':<20} {'n':<4} {'Succ@1':<8} {'Succ@2':<8} {'Succ@3':<8} "
          f"{'RepairCost':<11} {'Tokens':<8} {'Runtime':<9}")
    for label, agg in master["comparison_table"].items():
        n = agg.get("n_samples", 0)
        s1 = agg.get("Success@1", 0)
        s2 = agg.get("Success@2", 0)
        s3 = agg.get("Success@3", 0)
        rc = agg.get("MeanRepairCost", 0)
        tk = agg.get("MeanTotalTokens", 0)
        rt = agg.get("MeanRuntimeCost_s", 0)
        print(f"{label:<20} {n:<4} {s1:<8.2%} {s2:<8.2%} {s3:<8.2%} "
              f"{rc:<11.2f} {tk:<8.0f} {rt:<9.2f}")


if __name__ == "__main__":
    main()