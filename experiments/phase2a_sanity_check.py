"""Phase 2A Task A1.6 — sanity check cad_runtime on existing
reconstruction_engine scripts.  Verifies that the no-IR path
works on cadquery scripts we already know are good.

This is a SUB-AGENT to verify the executor on multiple scripts.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cad_runtime"))

from cad_runtime import execute_cad_script

CLEAN = ROOT / "Reconstruction_results"
OUT = ROOT / "experiments" / "phase2a_sanity"
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = OUT / "sanity_summary.json"


def read_script(sid: str) -> str:
    p = CLEAN / sid / "generated_code.py"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def main():
    sids = sorted([s for s in os.listdir(CLEAN)
                    if not s.endswith(".json") and s != "frozen_v0.1"])
    print(f"Found {len(sids)} samples with potential generated_code.py")
    results = []
    n_ok = 0
    n_step = 0
    n_occt = 0
    for i, sid in enumerate(sids):
        script = read_script(sid)
        if script is None:
            continue
        out_dir = OUT / sid
        try:
            res = execute_cad_script(script, out_dir, out_step_name=f"{sid}.step",
                                       timeout=60)
        except Exception as e:
            res = {"compile_status": False, "execution_status": False,
                    "step_export": False, "occt_load": False,
                    "runtime_error": f"{type(e).__name__}: {e}"}
        rec = {
            "sample_id": sid,
            "compile_status": res["compile_status"],
            "execution_status": res["execution_status"],
            "step_export": res["step_export"],
            "occt_load": res["occt_load"],
            "runtime_error": res["runtime_error"],
            "script_lines": len(script.splitlines()),
        }
        results.append(rec)
        if res["compile_status"]:
            n_ok += 1
        if res["step_export"]:
            n_step += 1
        if res["occt_load"]:
            n_occt += 1
        if (i + 1) % 10 == 0 or i + 1 == len(sids):
            print(f"  [{i+1}/{len(sids)}] OK={n_ok} STEP={n_step} OCCT={n_occt}")
    # Write summary
    summary = {
        "n_total": len(results),
        "n_compile_ok": n_ok,
        "n_step_ok": n_step,
        "n_occt_ok": n_occt,
        "results": results,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\nWrote {SUMMARY}")
    print(f"  Total: {len(results)} scripts")
    print(f"  Compile OK: {n_ok}/{len(results)}")
    print(f"  STEP export: {n_step}/{len(results)}")
    print(f"  OCCT load:   {n_occt}/{len(results)}")
    # Show some errors for debugging
    n_errors = sum(1 for r in results if r["runtime_error"])
    if n_errors:
        print(f"  Runtime errors: {n_errors} (showing first 5)")
        for r in results[:50]:
            if r["runtime_error"]:
                print(f"    - {r['sample_id']}: {r['runtime_error'][:120]}")


if __name__ == "__main__":
    main()
