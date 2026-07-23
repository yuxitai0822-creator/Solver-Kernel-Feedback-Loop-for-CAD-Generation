"""compute_clean_bbox.py — Compute bbox (X, Y, Z) for all 46 clean samples.

Uses OCP (cad_subproject1 env has OCP).  Reads each sample's
``Reconstruction_results/<sid>/generated.step`` and writes a
``reconstruction_bbox.json`` to ``task5_negative_perturbation/reports/``.

Per sample, emits: {bbox_mm: [x, y, z], volume: float}.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # .../task5_negative_perturbation/compute_clean_bbox.py → parents[1] = project root
sys.path.insert(0, str(ROOT))

from OCP.BRepBndLib import BRepBndLib
from OCP.STEPControl import STEPControl_Reader
from OCP.Bnd import Bnd_Box

# Look for clean_reconstruction_set.json in any of the known locations.
_candidates = [
    ROOT / "Reconstruction_results" / "frozen_v0.1" / "clean_reconstruction_set.json",
    ROOT / "Reconstruction_results" / "clean_reconstruction_set.json",
    ROOT / "task5_negative_perturbation" / "inputs" / "clean_reconstruction_set.json",
]
CLEAN_SET = next((c for c in _candidates if c.exists()), _candidates[0])
OUT_PATH = ROOT / "task5_negative_perturbation" / "reports" / "reconstruction_bbox.json"


def compute_bbox(step_path: Path) -> tuple[list[float], float] | None:
    if not step_path.exists():
        return None
    try:
        reader = STEPControl_Reader()
        reader.ReadFile(str(step_path))
        reader.TransferRoots()
        shape = reader.OneShape()
        if shape.IsNull():
            return None
        b = Bnd_Box()
        BRepBndLib.Add_s(shape, b)
        mn, mx = b.CornerMin(), b.CornerMax()
        bbox = [round(mx.X() - mn.X(), 4),
                  round(mx.Y() - mn.Y(), 4),
                  round(mx.Z() - mn.Z(), 4)]
        volume = round((mx.X() - mn.X()) * (mx.Y() - mn.Y()) * (mx.Z() - mn.Z()), 4)
        return bbox, volume
    except Exception as e:
        print(f"  WARN {step_path.name}: {e}")
        return None


def main():
    with open(CLEAN_SET, encoding="utf-8") as f:
        clean_set = json.load(f)
    samples = [s["sample_id"] for s in clean_set["clean_samples"]]
    results = {}
    n_ok = 0
    n_fail = 0
    for i, sid in enumerate(samples):
        step_path = ROOT / "Reconstruction_results" / sid / "generated.step"
        result = compute_bbox(step_path)
        if result is None:
            n_fail += 1
            results[sid] = None
            print(f"  [{i+1}/{len(samples)}] {sid}: FAIL")
            continue
        bbox, vol = result
        n_ok += 1
        results[sid] = {"bbox_mm": bbox, "volume": vol}
        print(f"  [{i+1}/{len(samples)}] {sid}: bbox=({bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f}) mm, vol={vol:.1f}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nwrote {OUT_PATH}")
    print(f"summary: {n_ok}/{len(samples)} samples have bbox ({n_fail} failed)")


if __name__ == "__main__":
    main()
