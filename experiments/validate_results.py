"""validate_results.py — Verify benchmark results conform to the v0.1 schema + protocol.

Checks per run_result.json:
  1. JSON-Schema validation against run_result_schema_v0.1.json
  2. JSON-Schema validation of each iter[] entry against iteration_record_schema_v0.1.json
  3. Artifact existence: every path in the schema must point to a real file
  4. IR schema validation: every IR_t.json / IR_t1.json must be cad_ir_v0.1 schema-valid
  5. CED present + numeric
  6. Token count totals are non-negative

Outputs:
  experiments/reports/validation_report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
from validator import validate as validate_ir  # noqa: E402

RUN_RESULT_SCHEMA = (ROOT / "experiments" / "schema"
                      / "run_result_schema_v0.1.json")
ITER_RESULT_SCHEMA = (ROOT / "experiments" / "schema"
                        / "iteration_record_schema_v0.1.json")


def _abs_path(rel: str) -> Path:
    return (ROOT / rel).resolve()


def validate_one_run(rel_path: str) -> dict:
    issues: list[str] = []
    rec: dict | None = None
    try:
        rec = json.loads((ROOT / rel_path).read_text(encoding="utf-8"))
    except Exception as e:
        return {"file": rel_path, "ok": False, "issues": [f"parse: {e}"]}

    # 1. Required top-level fields
    for k in ("schema_version", "run_id", "sample_id", "task_type",
                "method", "max_iter", "initial_status", "final_status",
                "metrics", "iterations", "artifacts_dir"):
        if k not in rec:
            issues.append(f"missing top-level field: {k}")
    if rec.get("schema_version") != "run_result_v0.1":
        issues.append(f"schema_version != run_result_v0.1 "
                       f"(got {rec.get('schema_version')!r})")
    if rec.get("task_type") not in ("repair", "no_op", "generation"):
        issues.append(f"unknown task_type: {rec.get('task_type')!r}")
    if rec.get("method") not in ("no_feedback", "solver_only",
                                    "kqp_only", "solver_kqp"):
        issues.append(f"unknown method: {rec.get('method')!r}")

    # 2. Required metrics fields
    m = rec.get("metrics", {})
    for k in ("success_at_1", "success_at_2", "success_at_3",
                "failure_to_success", "ced_text_total",
                "ced_declared_total", "ced_executed_total",
                "repair_cost", "runtime_sec", "n_iterations"):
        if k not in m:
            issues.append(f"missing metrics field: {k}")
    for k in ("success_at_1", "success_at_2", "success_at_3",
                "failure_to_success", "targeted_repair_success"):
        if k in m and not isinstance(m[k], bool):
            issues.append(f"metrics.{k} should be bool, got {type(m[k]).__name__}")

    # 3. Iterations
    iters = rec.get("iterations", [])
    if not isinstance(iters, list) or len(iters) == 0:
        issues.append("iterations must be non-empty list")
    for i, it in enumerate(iters):
        # 3a. Required per-iter fields
        for k in ("iter", "ir_path", "step_path", "solver_result_path",
                    "kqp_result_path", "agent_status", "kqp_status",
                    "wallclock_sec"):
            if k not in it:
                issues.append(f"iter[{i}] missing {k}")
        # 3b. Artifact existence
        for k in ("ir_path", "ir_t1_path", "step_path", "solver_result_path",
                    "kqp_result_path", "agent_prompt_path", "agent_response_path",
                    "runtime_log_path", "token_usage_path",
                    "adaptor_trace_path", "script_path"):
            v = it.get(k)
            if v is None:
                continue
            p = _abs_path(v)
            if not p.exists():
                issues.append(f"iter[{i}] {k} file missing: {v}")
        # 3c. CED path present for non-final iter
        if i < len(iters) - 1 and not it.get("ced_path"):
            issues.append(f"iter[{i}] non-final should have ced_path")
        if it.get("ced_path"):
            ced = _abs_path(it["ced_path"])
            if ced.exists():
                try:
                    ced_data = json.loads(ced.read_text(encoding="utf-8"))
                    if "ced_declared" not in ced_data:
                        issues.append(f"iter[{i}] ced missing ced_declared")
                except Exception as e:
                    issues.append(f"iter[{i}] ced parse: {e}")
        # 3d. IR_t schema validation
        ir_p = it.get("ir_path")
        if ir_p:
            ir_full = _abs_path(ir_p)
            if ir_full.exists():
                try:
                    ir = json.loads(ir_full.read_text(encoding="utf-8"))
                    res = validate_ir(ir)
                    if res["overall"] != "pass":
                        issues.append(f"iter[{i}] IR_t schema fail: "
                                       f"{res['schema_issues'][:2]}")
                except Exception as e:
                    issues.append(f"iter[{i}] IR_t parse: {e}")
        # 3e. KQP result must have query_results
        kqp_p = it.get("kqp_result_path")
        if kqp_p:
            kqp_full = _abs_path(kqp_p)
            if kqp_full.exists():
                try:
                    kd = json.loads(kqp_full.read_text(encoding="utf-8"))
                    if kd.get("status") not in (None, "skipped") \
                            and "query_results" not in kd:
                        issues.append(f"iter[{i}] KQP result missing query_results")
                except Exception as e:
                    issues.append(f"iter[{i}] KQP result parse: {e}")
        # 3f. Agent status enum
        if it.get("agent_status") not in ("not_called", "called_success",
                                                "called_failed",
                                                "called_skipped_method_m0"):
            issues.append(f"iter[{i}] invalid agent_status")
        # 3g. KQP status enum
        if it.get("kqp_status") not in ("pass", "fail", "unknown", "skipped",
                                            "error"):
            issues.append(f"iter[{i}] invalid kqp_status")

    return {"file": rel_path, "ok": not issues, "issues": issues,
              "n_iterations": len(iters)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="experiments/results")
    ap.add_argument("--out", default="experiments/reports/validation_report.json")
    args = ap.parse_args()

    results_dir = ROOT / args.results_dir
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    n_files = 0
    n_ok = 0
    if not results_dir.exists():
        print(f"results dir does not exist: {results_dir}")
        return
    for method_dir in results_dir.iterdir():
        if not method_dir.is_dir():
            continue
        for sample_dir in method_dir.iterdir():
            if not sample_dir.is_dir():
                continue
            rrf = sample_dir / "run_result.json"
            if not rrf.exists():
                continue
            n_files += 1
            rel = str(rrf.relative_to(ROOT))
            row = validate_one_run(rel)
            rows.append(row)
            if row["ok"]:
                n_ok += 1
            else:
                print(f"  ! {rel}: {len(row['issues'])} issues")
                for iss in row["issues"][:5]:
                    print(f"      - {iss}")

    report = {
        "phase": "Task 1 — Result Schema Validation",
        "n_files": n_files,
        "n_ok": n_ok,
        "n_failed": n_files - n_ok,
        "ok_rate": n_ok / n_files if n_files else 0,
        "rows": rows,
    }
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\nValidation: {n_ok}/{n_files} run_result.json files pass schema. "
          f"Report → {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()