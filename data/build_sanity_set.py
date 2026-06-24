"""Deterministically select the first 50 Phase0 (sanity) sequences and copy all
their files (json + every associated step/smt/obj/png) into data/sanity_set_50/.

Selection rule (identical to report.md Phase0):
  - only sketch + extrude entities
  - NO complex curves (spline/ellipse/elliptical-arc/conic)
  - 1 or 2 sketches
  - exactly 1 extrude
  - <= 8 curves per sketch

Determinism: iterate sequence ids in sorted order; take the first 50 that match.
Copy all files whose stem equals the seq id OR starts with "<seq_id>_" (the
operation-step snapshots). Output a manifest.json recording what was copied.
"""
import json
import shutil
from pathlib import Path

DATASET = Path(r"D:\dataset\r1.0.1\reconstruction")
OUT = Path(__file__).resolve().parent / "sanity_set_50"
MANIFEST = OUT / "manifest.json"

COMPLEX_CURVES = {
    "SketchFittedSpline", "SketchFixedSpline", "SketchEllipse",
    "SketchEllipticalArc", "SketchConicCurve",
}


def qualifies(fp):
    try:
        d = json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return False
    ents = d.get("entities", {})
    if not isinstance(ents, dict):
        return False
    sketches = [e for e in ents.values() if isinstance(e, dict) and e.get("type") == "Sketch"]
    extrudes = [e for e in ents.values() if isinstance(e, dict) and e.get("type") == "ExtrudeFeature"]
    # any non-sketch/non-extrude entity -> reject (pure sketch+extrude only)
    other = [e for e in ents.values() if isinstance(e, dict) and e.get("type") not in ("Sketch", "ExtrudeFeature")]
    if other:
        return False
    if not (1 <= len(sketches) <= 2):
        return False
    if len(extrudes) != 1:
        return False
    for s in sketches:
        curves = s.get("curves", {})
        if not isinstance(curves, dict) or len(curves) > 8:
            return False
        for c in curves.values():
            if isinstance(c, dict) and c.get("type") in COMPLEX_CURVES:
                return False
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # clear previous copy for reproducibility
    for p in OUT.iterdir():
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

    files = sorted(DATASET.glob("*.json"))
    selected = []
    for fp in files:
        if qualifies(fp):
            selected.append(fp.stem)
        if len(selected) == 50:
            break

    manifest = {"selection_rule": "sketch+extrude only; <=2 sketch; ==1 extrude; <=8 curves/sketch; no spline/ellipse/conic; first 50 by sorted id",
                "count": len(selected), "entries": []}

    for sid in selected:
        # copy json + all step/smt/obj/png for the seq and its op-step snapshots
        copied = {"id": sid, "files": []}
        for p in DATASET.iterdir():
            if p.is_file() and (p.stem == sid or p.stem.startswith(sid + "_")):
                dst = OUT / p.name
                shutil.copy2(p, dst)
                copied["files"].append({"name": p.name, "size": p.stat().st_size})
        manifest["entries"].append(copied)

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(e["files"]) for e in manifest["entries"])
    print(f"selected {len(selected)} sequences, copied {total} files to {OUT}")
    print("ids:")
    for s in selected:
        print(" ", s)


if __name__ == "__main__":
    main()
