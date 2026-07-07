"""perturb_history.py — Apply perturbation spec to a history JSON.

Pipeline
--------
    1. Load history JSON
    2. Detect profile type / extent type
    3. Apply operator → perturbed_history, perturbed_design_plan
    4. Run frozen ReconstructionEngine v0.1 → perturbed STEP
    5. Save perturbed_history.json + perturbation_meta.json + step_report
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "task5_negative_perturbation" / "perturbation"))

from operators import (all_operators, detect_profile_type,
                          detect_extent_type, parse_history)
from sampler import resolve_expected_queries


def apply_perturbation(history: dict, design_plan: dict,
                          spec: dict) -> tuple[dict, dict, dict]:
    """Run one operator and return (perturbed_history, perturbed_dp, meta)."""
    op_name = spec["operator"]
    params = spec.get("params", {}) or {}
    func = all_operators()[op_name]
    p_type = detect_profile_type(history)
    if op_name == "E3_radius_up" and p_type == "stadium":
        # Stadium arcs scale
        from operators import op_E3_radius as _e3
        ph, pd, m = _e3(history, design_plan, scale=1.25, target="arc")
    else:
        ph, pd, m = func(history, design_plan)
    # Annotate with sampler info
    m["perturbation_id"] = spec.get("perturbation_id")
    m["operator_input_name"] = op_name
    m["profile_type"] = p_type
    m["extent_type"] = detect_extent_type(history)
    return ph, pd, m


def run_reconstruct_engine(perturbed_history: dict, out_step_path: Path,
                              perturbed_dp: dict, design_plan_id: str
                              ) -> dict:
    """Run frozen ReconstructionEngine v0.1 on perturbed history → perturbed STEP.

    We re-use the orchestrator path but with a custom intermediate dir.
    """
    from reconstruction_engine.compiler import compile_history
    from reconstruction_engine.executor import execute_generated_code
    from kqp.runner.step_loader import load_step

    out_step_path.parent.mkdir(parents=True, exist_ok=True)

    # Persist perturbed history to a temp file in the same parent dir
    # so the compiler's _generate_code can use its filename for HISTORY_JSON.
    tmp_hist = out_step_path.parent / f"{design_plan_id}_perturbed.json"
    tmp_hist.write_text(json.dumps(perturbed_history, indent=2,
                                     ensure_ascii=False),
                          encoding="utf-8")

    # 1. Compile
    code, compile_report = compile_history(tmp_hist)

    # 2. Execute
    exec_report = execute_generated_code(code, out_step_path, tmp_hist)

    # 3. OCCT load
    if exec_report.get("export_success"):
        try:
            shape, status = load_step(out_step_path)
            occt_load_success = (shape is not None and not shape.IsNull())
        except Exception as e:
            occt_load_success = False
            status = f"load error: {e}"
    else:
        occt_load_success = False
        status = "skipped (export failed)"

    return {
        "compile_success": compile_report.get("compile_success", False),
        "execute_success": exec_report.get("execute_success", False),
        "export_success": exec_report.get("export_success", False),
        "occt_load_success": occt_load_success,
        "occt_load_status": status,
        "compile_unsupported_ops": compile_report.get("unsupported_ops", []),
        "execute_error": exec_report.get("error"),
        "execute_stderr_tail": (exec_report.get("stderr") or "")[-500:],
        "temp_history_path": str(tmp_hist),
    }


def save_perturbed_artifacts(out_dir: Path, perturbed_history: dict,
                                perturbed_design_plan: dict,
                                meta: dict, reconstruction_report: dict,
                                perturbed_step_path: Path | None = None,
                                original_step_path: Path | None = None
                                ) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "perturbed_history.json").write_text(
        json.dumps(perturbed_history, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (out_dir / "perturbed_design_plan.json").write_text(
        json.dumps(perturbed_design_plan, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (out_dir / "perturbation_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (out_dir / "reconstruction_report.json").write_text(
        json.dumps(reconstruction_report, indent=2, ensure_ascii=False),
        encoding="utf-8")
    if perturbed_step_path and Path(perturbed_step_path).exists():
        shutil.copy2(perturbed_step_path, out_dir / "generated.step")
    if original_step_path:
        # Save the original STEP path reference for later verification.
        (out_dir / "original_step_path.txt").write_text(
            str(original_step_path), encoding="utf-8")
