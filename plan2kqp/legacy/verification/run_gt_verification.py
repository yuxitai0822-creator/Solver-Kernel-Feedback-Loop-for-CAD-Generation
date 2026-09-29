"""run_gt_verification.py — Run KQP runner on all 50 GT STEPs.

For each sample:
1. Load the STEP file
2. Load the KQP instance (from KQP/samples/v0.2/)
3. Load the design_plan (from DesignPlan/compiler/instances_v6/) for frame
4. Run all queries
5. Collect results

Output: KQP/results/gt_verification/<sid>.result.json (50 files)
        KQP/results/gt_verification/_summary.json (aggregate report)
"""
from __future__ import annotations
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "kqp" / "runner"))

from run_kqp import run_kqp

STEP_DIR = ROOT / "data" / "sanity_set_50"
KQP_DIR = ROOT / "kqp" / "samples" / "v0.2"
PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"
OUT_DIR = ROOT / "kqp" / "results" / "gt_verification"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Get all sample IDs from KQP instances
    kqp_files = sorted(KQP_DIR.glob("*.kqp_instance.json"))
    print(f"Found {len(kqp_files)} KQP instances")

    results = []
    total_queries = 0
    passed_queries = 0
    failed_queries = 0
    error_queries = 0
    overall_pass = 0
    runner_success = 0
    crashed = []

    for kqp_path in kqp_files:
        sid = kqp_path.stem.replace(".kqp_instance", "")
        step_path = STEP_DIR / f"{sid}.step"
        plan_path = PLAN_DIR / f"{sid}.design_plan.json"

        if not step_path.exists():
            print(f"  [SKIP] {sid}: STEP not found")
            crashed.append({"sample_id": sid, "error": "STEP file not found"})
            continue

        try:
            kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
            plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else None

            result = run_kqp(step_path, kqp, plan)

            # Save individual result
            out_path = OUT_DIR / f"{sid}.result.json"
            out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

            runner_success += 1
            s = result["summary"]
            total_queries += s["total_queries"]
            passed_queries += s["passed_queries"]
            failed_queries += s["failed_queries"]
            error_queries += s.get("error_queries", 0)
            if result["overall_status"] == "pass":
                overall_pass += 1

            status_icon = "✓" if result["overall_status"] == "pass" else "✗"
            print(f"  {status_icon} {sid}: {result['overall_status']} "
                  f"({s['passed_queries']}/{s['total_queries']} pass"
                  + (f", {s['failed_queries']} fail" if s['failed_queries'] else "")
                  + (f", {s.get('error_queries',0)} err" if s.get('error_queries',0) else "")
                  + ")")

            if result["overall_status"] != "pass":
                for qr in result["query_results"]:
                    if qr["status"] != "pass":
                        print(f"      FAIL: {qr['query_id']} expected={qr['expected']} actual={qr['actual']} tol={qr['tolerance']}")

        except Exception as e:
            crashed.append({"sample_id": sid, "error": str(e), "tb": traceback.format_exc()})
            print(f"  ✗ {sid}: CRASH - {e}")

    # Summary
    summary = {
        "total_samples": len(kqp_files),
        "runner_success": runner_success,
        "overall_pass": overall_pass,
        "total_queries": total_queries,
        "passed_queries": passed_queries,
        "failed_queries": failed_queries,
        "error_queries": error_queries,
        "unsupported_queries": 0,
        "crashed_samples": crashed,
    }

    summary_path = OUT_DIR / "_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print("=" * 70)
    print("GT VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"  Total samples:     {summary['total_samples']}")
    print(f"  Runner success:    {summary['runner_success']}")
    print(f"  Overall pass:      {summary['overall_pass']}")
    print(f"  Total queries:     {summary['total_queries']}")
    print(f"  Passed queries:    {summary['passed_queries']}")
    print(f"  Failed queries:    {summary['failed_queries']}")
    print(f"  Error queries:     {summary['error_queries']}")
    print(f"  Unsupported:       {summary['unsupported_queries']}")
    print(f"  Crashed samples:   {len(summary['crashed_samples'])}")
    if crashed:
        for c in crashed:
            print(f"    {c['sample_id']}: {c['error']}")
    print(f"\n  Report: {summary_path}")


if __name__ == "__main__":
    main()
