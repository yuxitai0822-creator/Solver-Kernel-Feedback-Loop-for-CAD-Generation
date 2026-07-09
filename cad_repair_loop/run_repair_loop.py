"""run_repair_loop.py — CLI to run the repair loop on a batch of samples.

Usage:
  python run_repair_loop.py [samples_list] [output_root]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_repair_loop"))

import sys, importlib
sys.path.insert(0, str(Path(__file__).resolve().parent))
_repair_mod = importlib.import_module("repair_loop")
run_repair_loop = _repair_mod.run_repair_loop


def main():
    examples_dir = ROOT / "cad_ir" / "samples" / "manual_ir_examples"
    output_root = ROOT / "cad_repair_loop" / "results"

    summary_rows = []
    files = sorted(examples_dir.glob("*.cad_ir.json"))
    for f in files[:5]:  # Pilot run on 5 samples to validate the pipeline
        ir = json.loads(f.read_text(encoding="utf-8"))
        sid = ir["sample_id"]
        out = output_root / sid
        out.mkdir(parents=True, exist_ok=True)
        # The design plan is recovered from the IR (proxy: use IR as DP context)
        design_plan = {
            "sample_id": sid,
            "solid_bodies": [
                {"name": sid, "profiles": [{"type": ir["operations"][0]["op_type"]}],
                  "dimensions": {"extrude_distance":
                                    {"value": next((op["params"]["distance"]
                                                     for op in ir["operations"]
                                                     if op["op_type"] == "extrude"),
                                                   0)}}}
            ]
        }
        try:
            rep = run_repair_loop(ir, design_plan, out,
                                    max_iterations=3, agent_mode="offline")
            summary_rows.append({"sample_id": sid,
                                   "n_iterations": rep["n_iterations"],
                                   "n_execution_attempts": rep["n_execution_attempts"],
                                   "n_verification_calls": rep["n_verification_calls"],
                                   "ced_sum_raw": rep["ced_sum_raw"],
                                   "repair_cost": round(rep["repair_cost"], 3),
                                   "final_status": rep["final_status"]})
        except Exception as e:
            summary_rows.append({"sample_id": sid, "error": str(e)})

    out_path = ROOT / "cad_repair_loop" / "results" / "repair_loop_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"total": len(summary_rows),
                     "rows": summary_rows}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(json.dumps(summary_rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()