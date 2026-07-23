"""compile_kqp.py — CLI entry point for the KQP compiler.

Usage:
    python compile_kqp.py <design_plan_v0.6.json> [-o <output_kqp_instance.json>]
    python compile_kqp.py --batch  # compile all 50 sample designs (uses manifest)

Output: a v0.2 KQP instance JSON.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_reader import PlanReader
from query_builder import build_queries


KQP_SCHEMA_VERSION = "kqp_instance_v0.2"


def compile_one(plan_path: Path) -> dict:
    pr = PlanReader.from_file(plan_path)
    queries = build_queries(pr)
    return {
        "schema_version": KQP_SCHEMA_VERSION,
        "instance_id": f"kqp_{pr.sample_id}",
        "design_plan_id": pr.sample_id,
        "step_file": pr.step_file,
        "queries": queries,
    }


def compile_batch(plan_dir: Path, out_dir: Path) -> list[dict]:
    """Compile all design_plan_v0.6.json in plan_dir to KQP instances in out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for plan_path in sorted(plan_dir.glob("*.design_plan.json")):
        instance = compile_one(plan_path)
        out_path = out_dir / f"{instance['design_plan_id']}.kqp_instance.json"
        out_path.write_text(json.dumps(instance, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        results.append({"sample_id": instance["design_plan_id"],
                        "n_queries": len(instance["queries"]),
                        "out": str(out_path)})
    return results


def main():
    p = argparse.ArgumentParser(description="KQP v0.2 compiler")
    p.add_argument("input", nargs="?", help="path to design_plan_v0.6.json")
    p.add_argument("-o", "--output", help="path to output kqp_instance.json")
    p.add_argument("--batch", action="store_true", help="compile all 50 samples")
    p.add_argument("--plan-dir", default="compiler/instances_v6",
                   help="design_plan_v0.6 directory for --batch")
    p.add_argument("--out-dir", default="KQP/outputs/compiler_v0.1",
                   help="output directory for --batch")
    args = p.parse_args()

    if args.batch:
        plan_dir = Path(args.plan_dir)
        out_dir = Path(args.out_dir)
        results = compile_batch(plan_dir, out_dir)
        print(f"Compiled {len(results)} samples -> {out_dir}")
        for r in results[:5]:
            print(f"  {r['sample_id']}: {r['n_queries']} queries")
        if len(results) > 5:
            print(f"  ... ({len(results)-5} more)")
    elif args.input:
        plan_path = Path(args.input)
        instance = compile_one(plan_path)
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = plan_path.with_suffix(".kqp_instance.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(instance, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"Compiled {plan_path} -> {out_path} ({len(instance['queries'])} queries)")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
