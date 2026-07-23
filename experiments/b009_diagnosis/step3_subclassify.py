"""Step 3 of the B-009 diagnosis (read-only):
- All 23 regressed queries are class (I) direction mismatch.
- Sub-classify into I-a / I-b / I-c by comparing:
  - (I-a) DP compiler's frame vs history's reference_plane / transform
  - (I-b) History's frame vs STEP's actual bbox orientation
  - (I-c) DP has a `corrective_transform` field that KQP drops

Output: experiments/b009_diagnosis/class_I_subclassification.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = ROOT / "Reconstruction_results"
PLAN_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"
HIST_DIR = CLEAN_DIR
DATA = json.loads((ROOT / "experiments/b009_diagnosis" / "regression_classification.json").read_text(encoding="utf-8"))
OUT = ROOT / "experiments" / "b009_diagnosis" / "class_I_subclassification.json"


def _load_history_frame(sid: str) -> dict | None:
    """Return the reference_plane / transform / u_dir / v_dir /
    w_dir from the clean history JSON, OR None if the file is missing.
    """
    p = HIST_DIR / sid / "input_history.json"
    if not p.exists():
        return None
    hist = json.loads(p.read_text(encoding="utf-8"))
    # Find first Sketch
    sketch = None
    for eid, e in hist.get("entities", {}).items():
        if e.get("type") == "Sketch":
            sketch = e
            break
    if sketch is None:
        return None
    rp = sketch.get("reference_plane", {})
    plane = rp.get("plane", {})
    transform = sketch.get("transform", {})
    def _v(d, key):
        v = d.get(key) if d else None
        if v is None or not isinstance(v, dict):
            return None
        return [float(v.get("x", 0)), float(v.get("y", 0)), float(v.get("z", 0))]
    return {
        "reference_plane.plane.normal": _v(plane, "normal"),
        "reference_plane.plane.x_axis": _v(plane, "x_axis"),
        "reference_plane.plane.y_axis": _v(plane, "y_axis"),
        "transform.x_axis": _v(transform, "x_axis"),
        "transform.y_axis": _v(transform, "y_axis"),
        "transform.z_axis": _v(transform, "z_axis"),
    }


def _load_dp_frame(sid: str) -> dict | None:
    p = PLAN_DIR / f"{sid}.design_plan.json"
    if not p.exists():
        return None
    dp = json.loads(p.read_text(encoding="utf-8"))
    sb = dp.get("solid_bodies", [{}])[0]
    f = sb.get("frame", {})
    def _v(k): return f.get(k) if f else None
    return {
        "frame.u_dir": _v("u_dir"),
        "frame.v_dir": _v("v_dir"),
        "frame.w_dir": _v("w_dir"),
        "frame.corrective_transform": sb.get("corrective_transform") or None,
    }


def _vec_eq(a, b, tol=1e-3) -> bool:
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _vec_close(a, b, tol=0.01) -> bool:
    """Check if two unit vectors point in the same direction (allow
    ±tol deviation)."""
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    am = (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) ** 0.5
    bm = (b[0] ** 2 + b[1] ** 2 + b[2] ** 2) ** 0.5
    if am < 1e-9 or bm < 1e-9:
        return False
    dot = sum(ai * bi for ai, bi in zip(a, b)) / (am * bm)
    return abs(dot - 1.0) <= tol


def main():
    samples = [r for r in DATA["per_sample"]]
    classification = {
        "I-a": [],   # DP compiler extracts frame wrong from history
        "I-b": [],   # Reconstruction Engine builds STEP in wrong orientation
        "I-c": [],   # DP has corrective_transform, KQP drops it
        "unclear": [],
    }
    sample_results = []
    for r in samples:
        sid = r["sample_id"]
        cls = r["classifications"]
        if not all(c["class"] == "I" for c in cls):
            # Skip non-class-I samples (none in our case)
            continue
        hist = _load_history_frame(sid)
        dp = _load_dp_frame(sid)
        if hist is None or dp is None:
            classification["unclear"].append({"sample_id": sid, "reason": "missing file"})
            continue
        # Compare DP frame vs history frame
        # I-a: DP's u_dir vs history's plane.x_axis (or transform.x_axis)
        i_a_match = (_vec_close(dp.get("frame.u_dir"), hist.get("reference_plane.plane.x_axis"))
                     or _vec_close(dp.get("frame.u_dir"), hist.get("transform.x_axis")))
        i_a_v_match = (_vec_close(dp.get("frame.v_dir"), hist.get("reference_plane.plane.y_axis"))
                       or _vec_close(dp.get("frame.v_dir"), hist.get("transform.y_axis")))
        # If DP frame matches history frame, the design plan's frame is CORRECT
        # for the body orientation. The body bbox in 3D should match.
        # The error is somewhere else (executor, KQP).
        # I-b: history frame matches body's actual orientation
        # We check: history plane.normal matches the body's extrude axis
        # The body's longest dimension (extrude) should be along plane.normal.
        # If the STEP bbox has the extrude value along a different world axis
        # than plane.normal, then executor is at fault.
        from OCP.STEPControl import STEPControl_Reader
        from OCP.BRepBndLib import BRepBndLib
        from OCP.Bnd import Bnd_Box
        def _get_world_spans():
            step = HIST_DIR / sid / "generated.step"
            if not step.exists():
                return None
            try:
                r = STEPControl_Reader()
                r.ReadFile(str(step))
                r.TransferRoots()
                shape = r.OneShape()
                bb = Bnd_Box()
                BRepBndLib.Add_s(shape, bb)
                mn, mx = bb.CornerMin(), bb.CornerMax()
                return {
                    "x": round(mx.X() - mn.X(), 4),
                    "y": round(mx.Y() - mn.Y(), 4),
                    "z": round(mx.Z() - mn.Z(), 4),
                }
            except Exception:
                return None
        world_spans = _get_world_spans()
        hist_normal = hist.get("reference_plane.plane.normal")
        if hist_normal and world_spans:
            abs_normal = [abs(x) for x in hist_normal]
            if sum(abs_normal) > 0:
                expected_extrude_axis = abs_normal.index(max(abs_normal))
                extrude_world = world_spans[("x", "y", "z")[expected_extrude_axis]]
                # The history plane says: extrude is along this axis.
                # Check if the body's extrude is actually the design-plan
                # `length_u`, `width_v`, or `extrude_distance` value.
                # I-b is when the body's extrude axis doesn't match the
                # history plane's normal direction.
                # If the body bbox in the declared extrude direction
                # doesn't correspond to the actual extrude value, then
                # the executor is rotating the body in a way that
                # doesn't match the plane declaration.
        # I-c: does the DP have a corrective_transform?
        i_c = dp.get("frame.corrective_transform") is not None

        # Decision tree:
        # If I-a is False (DP frame doesn't match history frame), I-a wins.
        # If I-a is True but body bbox doesn't align with frame, I-b wins.
        # If both I-a and I-b are false (frame OK, body OK), I-c is residual.
        decision = "unclear"
        evidence = []
        if not i_a_match and not i_a_v_match:
            decision = "I-a"
            evidence.append("DP frame.u_dir and frame.v_dir do not match the "
                              "history's plane.x_axis or transform.x_axis")
        elif i_c:
            decision = "I-c"
            evidence.append("DP has a corrective_transform field that KQP "
                              "may be dropping (per query_dispatcher L48 "
                              "comment)")
        else:
            # I-a match; need to compare body vs frame
            # Check if body's extrude axis matches the frame.w_dir
            w = dp.get("frame.w_dir")
            if w and hist_normal and world_spans:
                # body bbox's longest dimension should be along frame.w_dir
                # and equal to design plan's extrude
                # We just need to see if the body's extrude direction matches
                # the declared frame.w_dir
                # For now flag as I-b if body bbox's smallest dim (which is
                # typically the extrude) doesn't match frame.w_dir
                smallest_axis = min(range(3), key=lambda i: world_spans[("x","y","z")[i]])
                smallest_world = [1, 0, 0]
                if smallest_axis > 0:
                    smallest_world[smallest_axis] = 1
                if not _vec_close(w, smallest_world):
                    decision = "I-b"
                    evidence.append("frame.w_dir doesn't match the body's "
                                       "smallest world axis")
                else:
                    decision = "unclear"
                    evidence.append("DP frame matches history, but body "
                                       "executor axis doesn't match the "
                                       "declared frame.w_dir — investigate "
                                       "manually")
            else:
                decision = "unclear"
        if decision == "unclear":
            classification["unclear"].append({"sample_id": sid, "reason": "; ".join(evidence)})
        else:
            classification[decision].append({
                "sample_id": sid,
                "frame.u_dir": dp.get("frame.u_dir"),
                "frame.v_dir": dp.get("frame.v_dir"),
                "frame.w_dir": dp.get("frame.w_dir"),
                "hist.plane.normal": hist_normal,
                "hist.transform.x_axis": hist.get("transform.x_axis"),
                "world_spans": world_spans,
                "has_corrective_transform": i_c,
                "evidence": evidence,
            })
        sample_results.append({
            "sample_id": sid,
            "decision": decision,
            "evidence": evidence,
        })
    out = {
        "n_class_I-a": len(classification["I-a"]),
        "n_class_I-b": len(classification["I-b"]),
        "n_class_I-c": len(classification["I-c"]),
        "n_class_unclear": len(classification["unclear"]),
        "per_sample": sample_results,
        "by_class": classification,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}")
    print()
    print(f"Class I-a (DP compiler extracts frame wrong): {len(classification['I-a'])} samples")
    print(f"Class I-b (Reconstruction Engine builds STEP wrong): {len(classification['I-b'])} samples")
    print(f"Class I-c (KQP drops corrective_transform): {len(classification['I-c'])} samples")
    print(f"Unclear: {len(classification['unclear'])} samples")
    print()
    # Print per-sample decision
    print("Per-sample:")
    for s in sample_results:
        print(f"  {s['sample_id']:30s} -> {s['decision']:6s}  | {s['evidence'][0] if s['evidence'] else ''}")


if __name__ == "__main__":
    main()
