"""subprocess_bridge.py — Cross-env subprocess bridges for the repair loop.

The `freecad_sketcher` env has FreeCAD + ZHIPU_API_KEY but NO cadquery.
The `cad_subproject1` env has cadquery + OCCT but NO FreeCAD.

This module exposes two functions that route Phase 2 (Adaptor) and Phase 3
(KQP) calls to `cad_subproject1` via subprocess, so the repair loop can
run in `freecad_sketcher` and exercise all three feedback channels:
- FreeCAD Solver Feedback (in-process via Freecadsolver_feedback.core)
- KQP Feedback (subprocess via cad_subproject1)
- ZHIPU LLM Agent (in-process, env-agnostic)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Python interpreters
CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"
FREECAD_PYTHON = r"D:/Anaconda/envs/freecad_sketcher/python.exe"


# ---------------------------------------------------------------------------
# Adaptor bridge (Phase 2 — runs in cad_subproject1)
# ---------------------------------------------------------------------------

_ADAPTOR_BRIDGE_PATH = Path(__file__).resolve().parent / "_adaptor_subprocess.py"


def run_adaptor_subprocess(ir: dict, out_dir: Path) -> dict:
    """Run the Phase 2 adaptor in `cad_subproject1` subprocess.

    Args:
      ir: a cad_ir_v0.1 dict (must be JSON-serializable).
      out_dir: directory for the adaptor's output files (STEP, script, etc.).

    Returns the adapter_report dict.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    # Write the IR to a temp file so the subprocess can read it.
    ir_path = out_dir / "_ir_input.cad_ir.json"
    ir_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    report_path = out_dir / "adapter_report.json"

    # The worker writes its own IR_t (in case it mutated the path field).
    result = subprocess.run(
        [CADQUERY_PYTHON, str(_ADAPTOR_BRIDGE_PATH),
         str(ir_path), str(out_dir)],
        capture_output=True, text=True, timeout=120,
        cwd=str(ROOT),
    )

    if not report_path.exists():
        # Write a synthetic error report
        return {
            "sample_id": ir.get("sample_id", "unknown"),
            "schema_check": "fail",
            "semantic_validation": "fail",
            "adapter_status": "fail",
            "script_syntax_status": "fail",
            "execution_status": "fail",
            "step_export_status": "fail",
            "warnings": [f"subprocess rc={result.returncode}: {result.stderr[-500:]}"],
        }
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"sample_id": ir.get("sample_id", "unknown"),
                "adapter_status": "fail",
                "warnings": [f"could not parse report: {type(e).__name__}: {e}"]}


# ---------------------------------------------------------------------------
# KQP bridge (Phase 3 — runs in cad_subproject1 subprocess via the existing
# `kqp/runner/run_kqp.py` CLI)
# ---------------------------------------------------------------------------

def run_kqp_subprocess(step_path: Path, kqp_instance_path: Path,
                          design_plan_path: Path,
                          output_path: Path) -> dict:
    """Run the Phase 3 KQP feedback via the existing KQP runner subprocess.

    Args:
      step_path:        STEP file produced by the adaptor
      kqp_instance_path: KQP instance JSON (sample-specific)
      design_plan_path:  DesignPlan v0.6 JSON (sample-specific)
      output_path:       where to write the KQP feedback JSON
    Returns the kqp_feedback dict.
    """
    if not step_path.exists():
        return {"overall_status": "fail", "error": f"step_path missing: {step_path}"}
    if not kqp_instance_path.exists():
        return {"overall_status": "unknown", "query_results": [],
                "error": f"no KQP instance: {kqp_instance_path}"}

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # kqp/runner/run_kqp.py signature:
    #   python run_kqp.py <step_path> <kqp_instance>
    #   [--design-plan PLAN] [-o OUTPUT]
    cmd = [CADQUERY_PYTHON,
            str(ROOT / "kqp" / "runner" / "run_kqp.py"),
            str(step_path),
            str(kqp_instance_path)]
    if design_plan_path.exists():
        cmd.extend(["--design-plan", str(design_plan_path)])
    cmd.extend(["-o", str(output_path)])

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                            cwd=str(ROOT))

    if not output_path.exists():
        return {"overall_status": "fail", "query_results": [],
                "error": f"KQP subprocess failed: rc={proc.returncode}, "
                          f"stderr={proc.stderr[-500:]}"}

    try:
        return json.loads(output_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"overall_status": "fail", "query_results": [],
                "error": f"KQP output parse error: {type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Helper: locate the on-disk KQP instance + DesignPlan for a sample
# ---------------------------------------------------------------------------

def locate_kqp_artifacts(sample_id: str) -> tuple[Path | None, Path | None]:
    kqp = ROOT / "kqp" / "outputs" / "compiler_v0.1" / f"{sample_id}.kqp_instance.json"
    plan = ROOT / "DesignPlan" / "compiler" / "instances_v6" / f"{sample_id}.design_plan.json"
    return (kqp if kqp.exists() else None,
            plan if plan.exists() else None)