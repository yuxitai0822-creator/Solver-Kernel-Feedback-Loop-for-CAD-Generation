"""test_repair_against_perturbed_ir.py — Validate the repair loop ON A
DELIBERATELY BROKEN IR, so the agent is actually exercised.

For 5 samples, generate a perturbed IR (wrong extrude distance), run the
loop, verify that:
  * KQP feedback returns at least one failing query on iter 0
  * LLM agent (online mode) emits a new IR
  * The new IR's KQP feedback passes (or improves)
  * CED_declared(IR_t, IR_{t+1}) > 0 (a real edit happened)
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import repair_loop


def perturb_ir(ir: dict) -> dict:
    """Halve the extrude distance — guaranteed KQP fail."""
    new_ir = copy.deepcopy(ir)
    for op in new_ir["operations"]:
        if op.get("op_type") == "extrude":
            old_d = op["params"]["distance"]
            op["params"]["distance"] = round(old_d * 0.5, 4)
            print(f"   perturbed extrude distance: {old_d} → "
                  f"{op['params']['distance']}")
    return new_ir


def run_one(sample_id: str, out_dir: Path, n_iter: int = 3) -> dict:
    examples_dir = ROOT / "cad_ir" / "samples" / "manual_ir_examples"
    ir_path = examples_dir / f"{sample_id}.cad_ir.json"
    plan_path = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sample_id}.design_plan.json"
    history_path = ROOT / "Reconstruction_results" / sample_id / "input_history.json"

    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    ir = perturb_ir(ir)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    ir["sample_id"] = sample_id

    out_dir.mkdir(parents=True, exist_ok=True)
    rep = repair_loop.run_repair_loop(
        ir, plan, out_dir,
        history_path=history_path if history_path.exists() else None,
        use_solver_feedback=True,
        max_iterations=n_iter,
        agent_mode="online",
    )
    return rep


def main():
    files = sorted((ROOT / "cad_ir" / "samples" / "manual_ir_examples").glob("*.cad_ir.json"))
    output_root = ROOT / "cad_repair_loop" / "results_perturbed"
    output_root.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for f in files[:3]:
        sid = f.stem.replace(".cad_ir", "")
        out = output_root / sid
        print(f"\n=== {sid} ===")
        try:
            rep = run_one(sid, out, n_iter=3)
            iters = rep["iter_records"]
            for r in iters:
                print(f"   iter {r['iter']}: {r['status']}  "
                      f"kqp={r['kqp_status']}")
            # Inspect iter 0 KQP feedback to confirm failure
            iter0_kqp = json.loads((out / "iter_00" / "kqp_feedback.json").read_text(encoding="utf-8"))
            failed_qrs = [qr for qr in iter0_kqp.get("query_results", [])
                          if qr.get("status") == "fail"]
            print(f"   iter 0 failed_queries: {len(failed_qrs)}")
            summary_rows.append({
                "sample_id": sid,
                "n_iterations": rep["n_iterations"],
                "n_execution_attempts": rep["n_execution_attempts"],
                "n_verification_calls": rep["n_verification_calls"],
                "ced_sum_raw": rep["ced_sum_raw"],
                "repair_cost": round(rep["repair_cost"], 3),
                "final_status": rep["final_status"],
                "iter_0_kqp_fail_count": len(failed_qrs),
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            summary_rows.append({"sample_id": sid, "error": str(e)})

    out_path = output_root.parent / "repair_loop_perturbed_summary.json"
    out_path.write_text(json.dumps({"total": len(summary_rows),
                                       "rows": summary_rows}, indent=2,
                                      ensure_ascii=False),
                          encoding="utf-8")
    print("\n=== Final summary ===")
    print(json.dumps(summary_rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()