"""Step 1 of the B-009 diagnosis (read-only):
- Run frame-only KQP on all 50 clean samples
- Identify the 15 regressing samples
- Per-query record: expected, frame_dir, frame_axis_span, world_spans, bestmatch_picked

Does NOT modify the frozen query_dispatcher.py — instead, inlines the
frame-only logic as a local function.

Output: experiments/b009_diagnosis/regressed_samples.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kqp" / "runner"))

import geometry_backend as gb
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box


CLEAN_DIR = ROOT / "Reconstruction_results"
PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"
KQP_DIR = ROOT / "kqp" / "outputs" / "compiler_v0.2"
OUT = ROOT / "experiments" / "b009_diagnosis" / "regressed_samples.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def frame_only_bbox(shape, axis, u_dir, v_dir, w_dir):
    """Frame-axis projection — what B-009 fix attempt 1 used."""
    return gb.get_bbox_size_along_frame_axis(shape, axis, u_dir, v_dir, w_dir)


def best_match_bbox(shape, axis, expected):
    """The original pre-fix KQP logic — pick closest world axis."""
    xmin, ymin, zmin, xmax, ymax, zmax = gb.get_axis_aligned_bbox(shape)
    world_spans = {"x": xmax - xmin, "y": ymax - ymin, "z": zmax - zmin}
    best = None
    best_diff = float("inf")
    best_axis = None
    for ax, ws in world_spans.items():
        d = abs(ws - expected)
        if d < best_diff:
            best_diff = d
            best = ws
            best_axis = ax
    return best, best_axis


def load_shape(step_path: Path):
    r = STEPControl_Reader()
    r.ReadFile(str(step_path))
    r.TransferRoots()
    return r.OneShape()


def main():
    sids = sorted([s for s in os.listdir(CLEAN_DIR)
                    if not s.endswith(".json") and s != "frozen_v0.1"])
    sids = [s for s in sids if (CLEAN_DIR / s / "generated.step").exists()
            and (PLAN_DIR / f"{s}.design_plan.json").exists()
            and (KQP_DIR / f"{s}.kqp_instance.json").exists()]

    print(f"Found {len(sids)} samples with all required files.")
    print()

    regressed = []
    bestmatch_pass = 0
    frameonly_pass = 0
    for sid in sids:
        step_path = CLEAN_DIR / sid / "generated.step"
        kqp_inst = json.loads((KQP_DIR / f"{sid}.kqp_instance.json").read_text(
            encoding="utf-8"))
        plan = json.loads((PLAN_DIR / f"{sid}.design_plan.json").read_text(
            encoding="utf-8"))

        # Get frame
        sb = plan.get("solid_bodies", [{}])[0]
        frame = sb.get("frame", {})
        u_dir = frame.get("u_dir", [1, 0, 0])
        v_dir = frame.get("v_dir", [0, 1, 0])
        w_dir = frame.get("w_dir", [0, 0, 1])
        frame_dirs = {"u": u_dir, "v": v_dir, "w": w_dir}

        # Load shape
        try:
            shape = load_shape(step_path)
        except Exception as e:
            print(f"  {sid}: shape load failed: {e}")
            continue

        # Get bbox
        xmin, ymin, zmin, xmax, ymax, zmax = gb.get_axis_aligned_bbox(shape)
        world_spans = {"x": xmax - xmin, "y": ymax - ymin, "z": zmax - zmin}

        # Process each bbox query
        regressed_queries = []
        for q in kqp_inst.get("queries", []):
            if q.get("intent") != "bbox_size":
                continue
            axis = q.get("axis")
            expected = q.get("expected")
            tol = q.get("tolerance", 0.01)
            if axis not in ("u", "v", "w") or expected is None:
                continue

            frame_span = frame_only_bbox(shape, axis, u_dir, v_dir, w_dir)
            best_span, best_axis = best_match_bbox(shape, axis, expected)

            frame_pass = abs(frame_span - expected) <= max(tol * 50, 1.0)
            best_pass = abs(best_span - expected) <= max(tol * 50, 1.0)

            if not best_pass:
                # This is a pre-existing failure (already failed under
                # best-match too) — not part of the 15 regressions.
                pass
            elif not frame_pass and best_pass:
                # Frame-only regressed this query while best-match passed.
                regressed_queries.append({
                    "query_id": q.get("id"),
                    "expected": expected,
                    "tolerance": tol,
                    "frame_axis": axis,
                    "frame_dir": list(frame_dirs[axis]),
                    "frame_axis_span": round(frame_span, 4),
                    "world_spans": {k: round(v, 4) for k, v in world_spans.items()},
                    "bestmatch_axis": best_axis,
                    "bestmatch_span": round(best_span, 4),
                    "frame_pass_check": round(frame_span - expected, 4),
                    "best_pass_check": round(best_span - expected, 4),
                })
        if not regressed_queries:
            bestmatch_pass += 1
        else:
            frameonly_pass += 1
            regressed.append({
                "sample_id": sid,
                "n_regressed_queries": len(regressed_queries),
                "regressed_queries": regressed_queries,
            })
    print(f"best-match pass (no bbox query regressed): {bestmatch_pass} / {len(sids)}")
    print(f"frame-only pass (≥1 bbox query regressed): {frameonly_pass} / {len(sids)}")
    print(f"regressed samples count: {len(regressed)}")
    summary = {
        "n_clean": len(sids),
        "n_bestmatch_pass": bestmatch_pass,
        "n_frameonly_pass": frameonly_pass,
        "n_regressed": len(regressed),
        "regressed_samples": regressed,
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                      encoding="utf-8")
    print(f"\nWrote {OUT}")
    for r in regressed:
        print(f"  {r['sample_id']}: {r['n_regressed_queries']} regressed queries")


if __name__ == "__main__":
    main()
