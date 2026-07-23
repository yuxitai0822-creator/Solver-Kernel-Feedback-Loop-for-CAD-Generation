"""sampler_ex.py — Eligibility filter + sampling for EX1, EX2 perturbations.

Per ``doc/execution_level_perturbation_plan_v0.1.md`` §4.4, the
eligibility filter is the *single most important guard* — it prevents
a repeat of B-007 (invisible perturbation).  The filter is run on
all 46 clean samples and produces an ``ex_perturbation_summary.json``
with per-sample eligibility + chosen target plane / swap.

The eligibility logic uses the *clean* sample's reconstruction-engine
STEP bbox spans.  EX1 is eligible iff the three bbox spans are
sufficiently distinct; EX2 is eligible iff the two in-plane spans
(width, height) are sufficiently distinct.  Without the guard,
near-cubic or near-square samples would be accepted but their
perturbation would not be KQP-detectable (best-match strategy masks
the swap).
"""
from __future__ import annotations

import json
import os
import sys
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# Tunable: 5x tolerance (per plan §4.4) — anything tighter than this is
# "indistinguishable" for the KQP best-match strategy.  The KQP
# default tolerance is 0.05 mm (= 0.005 cm in history); 5x = 0.25 mm.
INVISIBLE_TOLERANCE_MM = 0.25


# ---------------------------------------------------------------------------
# Bbox reading (assumes STEP has been generated; we read from a json
# report that lists bbox X/Y/Z for the clean sample)
# ---------------------------------------------------------------------------

def get_clean_bbox_spans_mm(sample_id: str, kqp_dir: str | None = None
                                ) -> tuple[float, float, float] | None:
    """Read the clean sample's bbox X/Y/Z (mm) from the reconstruction
    engine's per-sample report.  Returns None if the report is missing.

    This is offline (no LLM) and fast.
    """
    if kqp_dir is None:
        kqp_dir = str(ROOT / "kqp" / "outputs" / "compiler_v0.1")
    # The reconstruction report is per sample; we use the KQP result
    # which is bundled with bbox queries.
    kqp_path = Path(kqp_dir) / f"{sample_id}.kqp_instance.json"
    if not kqp_path.exists():
        return None
    try:
        kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    # The KQP instance doesn't carry bbox; we get the bbox from the
    # reconstruction STEP report instead.  Fall through to a per-sample
    # report file written by run_task5_generation.
    return _bbox_from_reconstruction_report(sample_id)


def _bbox_from_reconstruction_report(sample_id: str) -> tuple[float, float, float] | None:
    """Read bbox from the task5 reconstruction report if available."""
    rec_path = ROOT / "task5_negative_perturbation" / "reports" / "reconstruction_bbox.json"
    if not rec_path.exists():
        return None
    try:
        report = json.loads(rec_path.read_text(encoding="utf-8"))
        spans = report.get(sample_id)
        if not spans:
            return None
        return tuple(spans.get("bbox_mm", [None, None, None]))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Eligibility functions
# ---------------------------------------------------------------------------

def ex1_eligible(bbox: tuple[float, float, float] | None) -> bool:
    """EX1 (plane swap) is KQP-detectable iff the three bbox spans are
    sufficiently distinct.  Two near-equal spans would be masked by the
    KQP best-match strategy (plan §2.1)."""
    if bbox is None or any(s is None for s in bbox):
        return False
    bx, by, bz = bbox
    # Sort; the smallest spread should be > 5× the invisible tolerance.
    sorted_spans = sorted([bx, by, bz])
    smallest_pair_gap = sorted_spans[1] - sorted_spans[0]
    return smallest_pair_gap > 5 * INVISIBLE_TOLERANCE_MM


def ex2_eligible(bbox: tuple[float, float, float] | None,
                  history: dict) -> bool:
    """EX2 (in-plane axis flip) is KQP-detectable iff the two in-plane
    spans differ by more than 5× the tolerance.  For a near-square
    profile, the swap is invisible."""
    if bbox is None or any(s is None for s in bbox):
        return False
    # The two in-plane spans depend on the plane orientation.  We use
    # the smallest and second-smallest of the 3 spans as a conservative
    # proxy (whichever are in-plane must differ).
    sorted_spans = sorted(bbox)
    return (sorted_spans[1] - sorted_spans[0]) > 5 * INVISIBLE_TOLERANCE_MM


# ---------------------------------------------------------------------------
# C-path filter: per-sample profile check (Phase 2B Task B2)
# ---------------------------------------------------------------------------
# For EX1, even with frame-only KQP, a square 2D profile is undetectable
# because the bbox SET is invariant under any plane swap (X/Y/Z values
# are just permuted, not changed).  This C-path filter excludes samples
# where the design plan's profile is square (length_u == width_v).  The
# filter is a runtime check on the design plan, not on the bbox, because
# the design plan carries the engineering intent that the bbox does not.

C_PATH_SQUARE_TOLERANCE_MM = 0.5


def _get_dp_2d_dims_mm(sample_id: str) -> tuple[float, float] | None:
    """Read ``length_u`` and ``width_v`` from the design plan's first
    profile.  The v0.2 schema places them at
    ``solid_bodies[0].dimensions.profiles[0].length_u.value``
    (with ``width_v.value`` in the same parent).
    """
    p = (ROOT / "DesignPlan" / "compiler" / "instances_v0.2"
         / f"{sample_id}.design_plan.json")
    if not p.exists():
        # Fallback to instances_v6 for legacy samples.
        p = (ROOT / "DesignPlan" / "compiler" / "instances_v6"
             / f"{sample_id}.design_plan.json")
    if not p.exists():
        return None
    try:
        plan = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    sb = plan.get("solid_bodies", [{}])[0]
    dims = sb.get("dimensions") or {}
    profs = dims.get("profiles") or [{}]
    prof = profs[0] if profs else {}
    def _val(d, *keys):
        for k in keys:
            v = d.get(k)
            if isinstance(v, dict):
                v = v.get("value")
            if isinstance(v, (int, float)):
                return float(v)
        return None
    length_u = _val(prof, "length_u", "length", "width")
    width_v = _val(prof, "width_v", "width", "height")
    if length_u is None or width_v is None:
        # Fallback: try the top-level profile bbox
        prof_top = (sb.get("profiles") or [{}])[0]
        bbox = prof_top.get("bbox_size", {}) or {}
        length_u = _val(bbox, "length_u", "length", "width")
        width_v = _val(bbox, "width_v", "width", "height")
    if length_u is None or width_v is None:
        return None
    return length_u, width_v


def is_non_square_profile(sample_id: str) -> bool:
    """True iff the design plan's profile 2D dims differ by more than
    C_PATH_SQUARE_TOLERANCE_MM.  Used as the EX1-specific guard
    (B-011 C-path)."""
    dims = _get_dp_2d_dims_mm(sample_id)
    if dims is None:
        return False  # unknown — be conservative, exclude
    length_u, width_v = dims
    return abs(length_u - width_v) > C_PATH_SQUARE_TOLERANCE_MM


# ---------------------------------------------------------------------------
# Eligibility scan over all 46 clean samples
# ---------------------------------------------------------------------------

def scan_eligibility(clean_samples: list[str] | None = None,
                       write_summary: bool = True) -> dict:
    """Return a per-sample eligibility dict; optionally write
    ex_perturbation_summary.json to task5_negative_perturbation/reports/."""
    if clean_samples is None:
        # Load from clean_reconstruction_set.json
        clean_set_path = ROOT / "Reconstruction_results" / "clean_reconstruction_set.json"
        with open(clean_set_path, encoding="utf-8") as f:
            clean_set = json.load(f)
        clean_samples = [s["sample_id"] for s in clean_set["clean_samples"]]

    results = {
        "n_total": len(clean_samples),
        "eligible": {"EX1": [], "EX2": []},
        "ineligible": {"EX1": [], "EX2": []},
        "no_bbox": [],
    }
    for sid in clean_samples:
        bbox = get_clean_bbox_spans_mm(sid)
        if bbox is None:
            results["no_bbox"].append(sid)
            continue
        for ex in ("EX1", "EX2"):
            if ex == "EX1":
                # Phase 2B B-011 C-path: skip samples whose 2D profile
                # is square (length_u == width_v).  EX1 is undetectable
                # on square bodies even with frame-only KQP, because
                # the bbox SET is invariant under any plane swap.
                if not is_non_square_profile(sid):
                    results["ineligible"][ex].append(
                        {"sample_id": sid, "bbox_mm": list(bbox),
                         "reason": "square_profile"})
                    continue
                ok = ex1_eligible(bbox)
            else:
                ok = ex2_eligible(bbox, None)
            if ok:
                results["eligible"][ex].append({"sample_id": sid, "bbox_mm": list(bbox)})
            else:
                results["ineligible"][ex].append({"sample_id": sid, "bbox_mm": list(bbox)})

    if write_summary:
        out_path = ROOT / "task5_negative_perturbation" / "reports" / "ex_perturbation_summary.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"wrote {out_path}")
    return results


if __name__ == "__main__":
    scan_eligibility()
    print("done")
