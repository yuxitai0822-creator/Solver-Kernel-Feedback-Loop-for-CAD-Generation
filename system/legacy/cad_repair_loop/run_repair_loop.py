"""run_repair_loop.py — CLI to run the repair loop on a batch of samples.

Loads:
  * IR_t                (from cad_ir/samples/manual_ir_examples/<sid>.cad_ir.json)
  * DesignPlan v0.6     (from DesignPlan/compiler/instances_v6/<sid>.design_plan.json)
  * Original history    (from Reconstruction_results/<sid>/input_history.json)

Usage:
  python run_repair_loop.py --agent-mode auto --n 5
  python run_repair_loop.py --agent-mode online --n 3  # requires ZHIPU_API_KEY
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import via package import (cad_repair_loop/repair_loop.py)
import repair_loop


def _resolve_paths(sample_id: str):
    ir_path = (ROOT / "cad_ir" / "samples" / "manual_ir_examples"
                / f"{sample_id}.cad_ir.json")
    plan_path = (ROOT / "DesignPlan" / "compiler" / "instances_v6"
                  / f"{sample_id}.design_plan.json")
    history_path = (ROOT / "Reconstruction_results" / sample_id
                     / "input_history.json")
    return ir_path, plan_path, history_path


def run_one(sample_id: str, out_dir: Path, *,
              max_iterations: int = 3, agent_mode: str = "auto",
              use_solver_feedback: bool = True) -> dict:
    ir_path, plan_path, history_path = _resolve_paths(sample_id)
    if not ir_path.exists():
        return {"sample_id": sample_id, "error": f"missing IR {ir_path}"}
    if not plan_path.exists():
        return {"sample_id": sample_id, "error": f"missing DesignPlan {plan_path}"}

    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    ir["sample_id"] = sample_id

    out_dir.mkdir(parents=True, exist_ok=True)
    rep = repair_loop.run_repair_loop(
        ir, plan, out_dir,
        history_path=history_path if history_path.exists() else None,
        use_solver_feedback=use_solver_feedback,
        max_iterations=max_iterations,
        agent_mode=agent_mode,
    )
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-mode", default="auto",
                      choices=["auto", "online", "offline"])
    ap.add_argument("--n", type=int, default=5,
                      help="first N samples from manual_ir_examples")
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--no-solver-feedback", action="store_true",
                      help="skip FreeCAD solver feedback")
    args = ap.parse_args()

    output_root = ROOT / "cad_repair_loop" / "results"
    output_root.mkdir(parents=True, exist_ok=True)

    files = sorted((ROOT / "cad_ir" / "samples" / "manual_ir_examples").glob("*.cad_ir.json"))
    files = files[:args.n]

    summary_rows = []
    for f in files:
        sid = f.stem.replace(".cad_ir", "")
        out = output_root / sid
        print(f"\n=== {sid} ===")
        try:
            rep = run_one(sid, out,
                            max_iterations=args.max_iterations,
                            agent_mode=args.agent_mode,
                            use_solver_feedback=not args.no_solver_feedback)
            status = rep.get("final_status")
            rc = rep.get("repair_cost")
            print(f"  iterations={rep.get('n_iterations')}  "
                  f"status={status}  RepairCost={rc:.3f}"
                  if isinstance(rc, (int, float)) else
                  f"  iterations={rep.get('n_iterations')}  status={status}")
            for r in rep.get("iter_records", []):
                print(f"    iter {r['iter']}: {r['status']}  "
                      f"kqp={r['kqp_status']}  solver={r['solver_status']}")
            summary_rows.append({
                "sample_id": sid,
                "n_iterations": rep.get("n_iterations"),
                "n_execution_attempts": rep.get("n_execution_attempts"),
                "n_verification_calls": rep.get("n_verification_calls"),
                "ced_sum_raw": rep.get("ced_sum_raw"),
                "repair_cost": round(rc, 3)
                                  if isinstance(rc, (int, float)) else None,
                "final_status": status,
                "agent_mode": args.agent_mode,
                "use_solver_feedback": not args.no_solver_feedback,
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            summary_rows.append({"sample_id": sid, "error": str(e)})

    out_path = output_root / "repair_loop_summary.json"
    out_path.write_text(
        json.dumps({"total": len(summary_rows),
                     "agent_mode": args.agent_mode,
                     "use_solver_feedback": not args.no_solver_feedback,
                     "rows": summary_rows}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print("\n=== Final summary ===")
    print(json.dumps(summary_rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()