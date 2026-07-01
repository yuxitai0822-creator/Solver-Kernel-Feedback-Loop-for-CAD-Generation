"""run_kqp.py — CLI entry point for the KQP Runner.

Usage:
    python run_kqp.py <step_file> <kqp_instance.json> [--design-plan <plan.json>] [-o <output.json>]

Inputs:
    step_file: path to the STEP file to verify
    kqp_instance: the KQP instance JSON (queries + expected values)
    design_plan: (optional) the design_plan_v0.6 JSON (provides frame u/v/w)

Output:
    A KQPResult JSON written to stdout or -o file.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import step_loader
import query_dispatcher
from result_builder import build_kqp_result


def run_kqp(step_path: str | Path, kqp_instance: dict, design_plan: dict | None = None) -> dict:
    """Run all KQP queries against a STEP file.

    Returns a KQPResult dict.
    """
    # 1. Load STEP
    shape, _ = step_loader.load_step(step_path)

    # 2. Extract frame from design_plan (if provided)
    frame = {"u_dir": [1, 0, 0], "v_dir": [0, 1, 0], "w_dir": [0, 0, 1]}
    if design_plan:
        sb = design_plan.get("solid_bodies", [{}])[0]
        f = sb.get("frame", {})
        frame["u_dir"] = f.get("u_dir", [1, 0, 0])
        frame["v_dir"] = f.get("v_dir", [0, 1, 0])
        frame["w_dir"] = f.get("w_dir", [0, 0, 1])

    # 3. Execute each query
    query_results = []
    for q in kqp_instance.get("queries", []):
        result = query_dispatcher.dispatch_query(shape, q, frame)
        # Augment with query metadata
        result["query_id"] = q.get("id", "")
        result["intent"] = q.get("intent", "")
        result["source_field"] = q.get("source_field", "")
        # Reorder keys for readability
        ordered = {
            "query_id": result.pop("query_id"),
            "intent": result.pop("intent"),
            "status": result.pop("status"),
            "expected": result.pop("expected"),
            "actual": result.pop("actual"),
            "tolerance": result.pop("tolerance"),
            "error": result.pop("error"),
            "source_field": result.pop("source_field"),
            "feedback": result.pop("feedback"),
        }
        query_results.append(ordered)

    # 4. Build result
    return build_kqp_result(
        sample_id=kqp_instance.get("design_plan_id", ""),
        kqp_schema_version=kqp_instance.get("schema_version", "kqp_instance_v0.2"),
        step_file=str(step_path),
        query_results=query_results,
    )


def main():
    p = argparse.ArgumentParser(description="KQP Runner — execute KQP queries on a STEP file")
    p.add_argument("step_file", help="path to STEP file")
    p.add_argument("kqp_instance", help="path to KQP instance JSON")
    p.add_argument("--design-plan", help="path to design_plan_v0.6 JSON (for frame extraction)")
    p.add_argument("-o", "--output", help="output result JSON path")
    args = p.parse_args()

    kqp = json.loads(Path(args.kqp_instance).read_text(encoding="utf-8"))
    plan = None
    if args.design_plan:
        plan = json.loads(Path(args.design_plan).read_text(encoding="utf-8"))

    result = run_kqp(args.step_file, kqp, plan)

    if args.output:
        out = Path(args.output)
    else:
        out = Path(args.kqp_instance).with_suffix(".result.json")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    status = result["overall_status"]
    s = result["summary"]
    print(f"{result['sample_id']}: {status} ({s['passed_queries']}/{s['total_queries']} queries pass)")
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
