"""dataset/triplet.py — One ``Verified Triplet`` per (sid, nid).

Composes the edit-code pair ``(Code_gt, Code_perturbed)`` together
with ``T_ref`` (the perturbation reference) and orchestrates the
three verification layers required by the M0-M3 perturbation
experiment:

  1.  Code execution verification  (both Code_gt and Code_perturbed
      must compile / execute / export STEP / load in OCCT).
  2.  Code_gt geometric fidelity  (CD(Code_gt.step, GT_history.step)
      < 1e-5 AND KQP queries pass on Code_gt.step).
  3.  Difference check            (KQP-flip-diff between Code_gt.step
      and Code_perturbed.step matches ``T_ref.expected_failed_query``
      and respects ``T_ref.allowed_secondary_failed_queries``).

The fall-back semantic-diff (LLM judge) described in the user spec
is not implemented here yet — it lives behind ``llm_semantic_diff``,
which is invoked only when the KQP difference check raises an
unrecoverable error.  See ``dataset/build_triplets.py`` for the
end-to-end entry point.

Outputs (per trial):

    experiments/phase2b_triplets/<sid>_<nid>/
        code_gt.py             # the GT code, copied through
        code_perturbed.py      # freshly compiled from perturbed history
        step_gt/               # re-executed GT step (sanity)
            generated.step
        step_perturbed/        # re-executed perturbed step
            generated.step
        triplet.json           # the verification record (passed/failed,
                                # plus numeric metrics)
"""
from __future__ import annotations

import dataclasses
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

# Project-level deps.  We do imports inside ``build_triplet`` to keep
# module import lazy (avoids loading OCCT at interpreter startup).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


GT_RESULTS_ROOT = _REPO_ROOT / "Reconstruction_results"
PERTURBATIONS_ROOT = _REPO_ROOT / "task5_negative_perturbation" / "perturbations"
KQP_ROOT = _REPO_ROOT / "kqp" / "outputs" / "compiler_v0.2"
DESIGN_PLAN_ROOT = _REPO_ROOT / "DesignPlan" / "compiler" / "instances_v6"

# Verifier thresholds
CD_FIDELITY_THRESHOLD = 1e-5     # spec: CD < 10^-5


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class TripletPaths:
    sid: str
    nid: str
    out_dir: Path
    code_gt:           Path
    code_perturbed:    Path
    step_gt_dir:       Path
    step_perturbed_dir: Path
    triplet_json:      Path


@dataclasses.dataclass
class Triplet:
    sid: str
    nid: str
    layer: str                    # TypeA / EX2 (we'll classify by nid format)
    T_ref: dict
    code_gt_path: str | None
    code_perturbed_path: str | None
    step_gt_path: str | None
    step_perturbed_path: str | None
    layer1_pipeline_gt: dict
    layer1_pipeline_perturbed: dict
    layer2_fidelity: dict
    layer3_difference: dict
    verified: bool
    wallclock: float
    notes: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# ---------------------------------------------------------------------------
# Helpers — file loaders
# ---------------------------------------------------------------------------
def _classify_layer(nid: str) -> str:
    """Map a perturbation directory name to ``TypeA`` or ``EX2``."""
    if nid.startswith("ex"):
        return "EX2"
    return "TypeA"


def _load_gt_paths(sid: str) -> tuple[Path, Path, Path] | None:
    """Locate the GT artefacts produced by ``reconstruct_sample``:
    ``generated_code.py``, ``generated.step``, and ``input_history.json``.

    Returns ``None`` if the reconstruction is missing for this sid.
    """
    code = GT_RESULTS_ROOT / sid / "generated_code.py"
    step = GT_RESULTS_ROOT / sid / "generated.step"
    history = GT_RESULTS_ROOT / sid / "input_history.json"
    if not (code.exists() and step.exists() and history.exists()):
        return None
    return code, step, history


def _load_perturbed_paths(sid: str, nid: str) -> tuple[Path, Path, Path] | None:
    """Locate the artefacts created by the perturbation pipeline.

    The pipeline writes:
      ``perturbed_history.json``   (perturbed Fusion360 history)
      ``perturbation_meta.json``   (T_ref)
      ``generated.step``          (reconstructed STEP from perturbed history)

    EX1 / EX2 perturbations do NOT always include ``perturbed_history.json``
    in the same directory layout, so this helper may return ``None``
    even when the (sid, nid) directory exists.
    """
    base = PERTURBATIONS_ROOT / sid / nid
    if not base.exists():
        return None
    history = base / "perturbed_history.json"
    meta = base / "perturbation_meta.json"
    step = base / "generated.step"
    if not history.exists() or not meta.exists():
        return None
    return history, meta, step


def _load_design_plan(sid: str) -> dict:
    p = DESIGN_PLAN_ROOT / f"{sid}.design_plan.json"
    if not p.exists():
        # Fallback for the v0.2 directory if v6 doesn't have it.
        p2 = _REPO_ROOT / "DesignPlan" / "compiler" / "instances_v0.2" / f"{sid}.design_plan.json"
        if p2.exists():
            p = p2
    return json.loads(p.read_text(encoding="utf-8"))


def _load_kqp(sid: str) -> dict:
    p = KQP_ROOT / f"{sid}.kqp_instance.json"
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Helpers — code compilation and execution
# ---------------------------------------------------------------------------
def _compile_perturbed(perturbed_history_path: Path,
                       out_path: Path) -> tuple[str | None, dict]:
    """Compile ``perturbed_history.json`` → CadQuery source via the
    existing reconstruction engine.

    Returns ``(code_string | None, compile_report)``.  ``code_string``
    is ``None`` when compilation failed.
    """
    import importlib.util as iu
    spec = iu.spec_from_file_location("reconstruction_engine_compiler",
                                       str(_REPO_ROOT / "reconstruction_engine" / "compiler.py"))
    mod = iu.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        return None, {"compile_success": False,
                       "compile_error": f"{type(e).__name__}: {e}"}
    try:
        code, report = mod.compile_history(perturbed_history_path)
    except Exception as e:  # noqa: BLE001
        return None, {"compile_success": False,
                       "compile_error": f"{type(e).__name__}: {str(e)[:300]}"}
    out_path.write_text(code, encoding="utf-8")
    return code, report


def _execute_script(script_path: Path,
                    out_dir: Path,
                    out_step_name: str = "generated.step",
                    timeout: int = 120) -> dict:
    """Run the script in a subprocess via the existing
    ``cad_runtime.executor.execute_cad_script``.

    The executor handles compile / execute / STEP export / OCCT load.
    """
    import importlib.util as iu
    spec = iu.spec_from_file_location("cad_runtime_executor",
                                       str(_REPO_ROOT / "cad_runtime" / "executor.py"))
    mod = iu.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    script = script_path.read_text(encoding="utf-8")
    return mod.execute_cad_script(script, out_dir,
                                    out_step_name=out_step_name, timeout=timeout)


# ---------------------------------------------------------------------------
# Helpers — KQP run
# ---------------------------------------------------------------------------
def _run_kqp(step_path: Path, kqp_instance: dict,
              design_plan: dict) -> dict:
    """Run the pre-computed KQP against a STEP file.

    Wraps ``kqp.runner.run_kqp.run_kqp`` so we get a uniform {status,
    actual, expected, error} per-query dict.
    """
    import importlib.util as iu
    spec = iu.spec_from_file_location("kqp_runner_run_kqp",
                                       str(_REPO_ROOT / "kqp" / "runner" / "run_kqp.py"))
    mod = iu.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.run_kqp(step_path, kqp_instance, design_plan)


# ---------------------------------------------------------------------------
# Helpers — verification logic
# ---------------------------------------------------------------------------
def _verify_layer1(pipeline_gt: dict, pipeline_perturbed: dict) -> dict:
    """Both scripts compile, execute, write STEP, and load OCCT.

    Both must succeed for layer 1 to pass.
    """
    gt_ok = all(pipeline_gt.get(k) for k in ("compile_status",
                                              "execution_status",
                                              "step_export",
                                              "occt_load"))
    pe_ok = all(pipeline_perturbed.get(k) for k in ("compile_status",
                                                     "execution_status",
                                                     "step_export",
                                                     "occt_load"))
    return {
        "passed": gt_ok and pe_ok,
        "code_gt": pipeline_gt,
        "code_perturbed": pipeline_perturbed,
    }


def _verify_layer2_fidelity(code_gt_step: Path | None,
                              gt_history_step: Path,
                              gt_kqp: dict | None) -> dict:
    """CD(Code_gt.step, GT_history.step) < 1e-5 AND KQP queries pass
    on Code_gt.step.

    Loads chamfer lazily so the helper is importable even when
    scipy / OCCT mesh is not available.
    """
    res: dict[str, Any] = {"passed": True, "checks": []}

    # 1. CD check.
    if code_gt_step is None or not code_gt_step.exists():
        res["passed"] = False
        res["checks"].append({"name": "cd", "status": "skipped",
                                 "reason": "code_gt_step missing"})
    else:
        try:
            from dataset.chamfer import file_chamfer_distance
            cd = file_chamfer_distance(code_gt_step, gt_history_step, n_points=2000)
            res["checks"].append({
                "name":   "cd",
                "status": "pass" if cd["chamfer_distance"] < CD_FIDELITY_THRESHOLD else "fail",
                "chamfer_distance": cd["chamfer_distance"],
                "min_distance":     cd["min_distance"],
                "threshold":        CD_FIDELITY_THRESHOLD,
            })
            if cd["chamfer_distance"] >= CD_FIDELITY_THRESHOLD:
                res["passed"] = False
        except Exception as e:  # noqa: BLE001
            res["checks"].append({"name": "cd", "status": "error",
                                    "exception": f"{type(e).__name__}: {e}"})
            res["passed"] = False

    # 2. KQP check.
    if gt_kqp is None:
        res["checks"].append({"name": "kqp", "status": "skipped",
                                "reason": "kqp_run_failed"})
        res["passed"] = False
    else:
        n_pass = sum(1 for q in gt_kqp.get("query_results", [])
                      if q.get("status") == "pass")
        n_total = len(gt_kqp.get("query_results", []))
        all_pass = (n_total > 0 and n_pass == n_total)
        res["checks"].append({
            "name":         "kqp",
            "status":       "pass" if all_pass else "fail",
            "passed":       n_pass,
            "total":        n_total,
            "overall_status": gt_kqp.get("overall_status"),
        })
        if not all_pass:
            res["passed"] = False

    return res


def _verify_layer3_difference(gt_kqp: dict | None,
                               perturbed_kqp: dict | None,
                               T_ref: dict) -> dict:
    """Compute the KQP-flip diff and validate against T_ref."""
    res: dict[str, Any] = {
        "passed":         True,
        "expected_failed":  T_ref.get("expected_failed_query", []),
        "allowed_secondary": T_ref.get("allowed_secondary_failed_queries", []),
        "actual_failed":   [],
        "unexpected_failed": [],
        "kqp_unavailable": False,
    }
    if gt_kqp is None or perturbed_kqp is None:
        res["passed"] = False
        res["kqp_unavailable"] = True
        return res

    # Build status maps.
    def _id_to_status(kqp: dict) -> dict[str, str]:
        m: dict[str, str] = {}
        for q in kqp.get("query_results", []):
            m[q.get("query_id", "?")] = q.get("status", "?")
        return m

    gt_status = _id_to_status(gt_kqp)
    pe_status = _id_to_status(perturbed_kqp)

    # Diff: queries that flipped from "pass" → "fail" are the
    # actual_failed set.
    actual_failed = sorted(qid for qid, s in pe_status.items()
                            if s != "pass" and gt_status.get(qid) == "pass")
    res["actual_failed"] = actual_failed

    expected = set(res["expected_failed"])
    allowed  = set(res["allowed_secondary"])
    actual   = set(actual_failed)

    # expected_failed queries should be in actual_failed.
    unexpected = sorted((actual - expected - allowed))
    res["unexpected_failed"] = unexpected

    # All expected queries should appear in the diff.
    missing_expected = sorted((expected - actual))
    res["missing_expected"] = missing_expected

    # An "extra" query (in actual but not in expected+allowed) is also
    # unexpected.
    extras = sorted((actual - expected - allowed))
    res["extras"] = extras
    res["passed"] = (not unexpected) and (not missing_expected) and (not extras)
    res["gt_status_per_query"] = gt_status
    res["perturbed_status_per_query"] = pe_status
    return res


# ---------------------------------------------------------------------------
# Main entry: build one Triplet
# ---------------------------------------------------------------------------
def build_triplet(sid: str,
                  nid: str,
                  out_root: Path = _REPO_ROOT / "experiments" / "phase2b_triplets",
                  timeout: int = 120) -> Triplet:
    """Compose a single Verified Triplet for ``(sid, nid)``.

    Returns a ``Triplet`` even on failure — ``verified`` is False
    and ``notes`` carries the human-readable summary.  The artefact
    tree is always written under ``out_root/<sid>_<nid>/``.
    """
    t0 = time.time()
    layer = _classify_layer(nid)

    # Where to put this trial's artefacts.
    base = Path(out_root) / f"{sid}__{nid}"
    base.mkdir(parents=True, exist_ok=True)
    paths = TripletPaths(
        sid=sid, nid=nid, out_dir=base,
        code_gt=base / "code_gt.py",
        code_perturbed=base / "code_perturbed.py",
        step_gt_dir=base / "step_gt",
        step_perturbed_dir=base / "step_perturbed",
        triplet_json=base / "triplet.json",
    )

    # ----- 1. Locate artefacts. -----
    gt = _load_gt_paths(sid)
    if gt is None:
        return Triplet(
            sid=sid, nid=nid, layer=layer, T_ref={},
            code_gt_path=None, code_perturbed_path=None,
            step_gt_path=None, step_perturbed_path=None,
            layer1_pipeline_gt={}, layer1_pipeline_perturbed={},
            layer2_fidelity={"passed": False, "checks": [
                {"name": "locate", "status": "fail",
                 "reason": "Reconstruction_results/<sid> missing required files"}]},
            layer3_difference={"passed": False, "reason": "upstream"},
            verified=False,
            wallclock=round(time.time() - t0, 2),
            notes="failed: GT reconstruction artefacts missing",
        )

    gt_code_path, gt_step_path, gt_history_path = gt
    per = _load_perturbed_paths(sid, nid)
    if per is None:
        return Triplet(
            sid=sid, nid=nid, layer=layer, T_ref={},
            code_gt_path=None, code_perturbed_path=None,
            step_gt_path=None, step_perturbed_path=None,
            layer1_pipeline_gt={}, layer1_pipeline_perturbed={},
            layer2_fidelity={"passed": False, "checks": [
                {"name": "locate", "status": "fail",
                 "reason": "perturbed directory missing perturbed_history.json "
                            "(this happens for some EX1/EX2 perturbations)"}]},
            layer3_difference={"passed": False, "reason": "upstream"},
            verified=False,
            wallclock=round(time.time() - t0, 2),
            notes="failed: perturbed_history.json missing",
        )
    perturbed_history_path, perturbed_meta_path, perturbed_step_path = per
    T_ref = json.loads(perturbed_meta_path.read_text(encoding="utf-8"))

    # Always copy the GT script (so the triplet directory is
    # self-contained even if the source moves).
    shutil.copy2(gt_code_path, paths.code_gt)

    # ----- 2. Copy / re-compile Code_perturbed. -----
    code_perturbed, compile_report = _compile_perturbed(
        perturbed_history_path, paths.code_perturbed)
    if code_perturbed is None:
        return Triplet(
            sid=sid, nid=nid, layer=layer, T_ref=T_ref,
            code_gt_path=str(paths.code_gt),
            code_perturbed_path=str(paths.code_perturbed),
            step_gt_path=str(gt_step_path),
            step_perturbed_path=None,
            layer1_pipeline_gt={}, layer1_pipeline_perturbed={"compile_error": compile_report},
            layer2_fidelity={"passed": False, "checks": [{"name": "compile_perturbed", "status": "fail",
                                                              "report": compile_report}]},
            layer3_difference={"passed": False, "reason": "upstream"},
            verified=False,
            wallclock=round(time.time() - t0, 2),
            notes="failed: perturbed code compilation failed",
        )

    # ----- 3. Re-execute both scripts (pipeline verification). -----
    paths.step_gt_dir.mkdir(parents=True, exist_ok=True)
    paths.step_perturbed_dir.mkdir(parents=True, exist_ok=True)
    try:
        pipeline_gt = _execute_script(gt_code_path, paths.step_gt_dir, timeout=timeout)
    except Exception as e:  # noqa: BLE001
        pipeline_gt = {"compile_status": False,
                        "execution_status": False,
                        "step_export": False,
                        "occt_load": False,
                        "runtime_error": f"runner_error: {type(e).__name__}: {e}",
                        "step_path": None}
    try:
        pipeline_perturbed = _execute_script(paths.code_perturbed, paths.step_perturbed_dir, timeout=timeout)
    except Exception as e:  # noqa: BLE001
        pipeline_perturbed = {"compile_status": False,
                                "execution_status": False,
                                "step_export": False,
                                "occt_load": False,
                                "runtime_error": f"runner_error: {type(e).__name__}: {e}",
                                "step_path": None}

    step_gt = pipeline_gt.get("step_path")
    step_pe = pipeline_perturbed.get("step_path")

    layer1 = _verify_layer1(pipeline_gt, pipeline_perturbed)

    # ----- 4. Layer 2: Code_gt fidelity. -----
    gt_kqp: dict | None = None
    pe_kqp: dict | None = None
    try:
        design_plan = _load_design_plan(sid)
        kqp_instance = _load_kqp(sid)
    except Exception as e:  # noqa: BLE001
        design_plan = {}
        kqp_instance = {"queries": []}

    if step_gt and Path(step_gt).exists():
        try:
            gt_kqp = _run_kqp(Path(step_gt), kqp_instance, design_plan)
        except Exception as e:  # noqa: BLE001
            gt_kqp = {"error": f"{type(e).__name__}: {e}"}
    # Use the existing kqp_result.json (perturbed) as a fast path; we
    # still recompute on our freshly-executed Code_perturbed step for
    # fidelity.  If the on-disk kqp_result.json matches our step path,
    # fall back to it.
    if step_pe and Path(step_pe).exists():
        try:
            pe_kqp = _run_kqp(Path(step_pe), kqp_instance, design_plan)
        except Exception as e:  # noqa: BLE001
            pe_kqp = {"error": f"{type(e).__name__}: {e}"}

    layer2 = _verify_layer2_fidelity(Path(step_gt) if step_gt else None,
                                      gt_step_path,
                                      gt_kqp)

    # ----- 5. Layer 3: difference check. -----
    layer3 = _verify_layer3_difference(gt_kqp, pe_kqp, T_ref)

    verified = bool(layer1["passed"] and layer2["passed"] and layer3["passed"])

    return Triplet(
        sid=sid, nid=nid, layer=layer, T_ref=T_ref,
        code_gt_path=str(paths.code_gt),
        code_perturbed_path=str(paths.code_perturbed),
        step_gt_path=step_gt,
        step_perturbed_path=step_pe,
        layer1_pipeline_gt=pipeline_gt,
        layer1_pipeline_perturbed=pipeline_perturbed,
        layer2_fidelity=layer2,
        layer3_difference=layer3,
        verified=verified,
        wallclock=round(time.time() - t0, 2),
        notes="ok" if verified else "see_checks",
    )


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------
def save_triplet(triplet: Triplet) -> Path:
    """Write the triplet JSON next to its artefact tree.  Returns
    the path to the JSON file."""
    out = Path(triplet.code_gt_path).parent / "triplet.json" \
        if triplet.code_gt_path else None
    if out is None:
        return None
    out.write_text(json.dumps(triplet.to_dict(), indent=2,
                                ensure_ascii=False, default=str),
                   encoding="utf-8")
    return out


__all__ = [
    "build_triplet",
    "save_triplet",
    "Triplet",
    "CD_FIDELITY_THRESHOLD",
]
