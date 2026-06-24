"""Derive candidate slices (Phase0/Phase1/Phase2) from the dataset.

Maps the experiment design's selection criteria onto the actual data:

Phase0 (Sanity, target 50): sketch+extrude only, NO spline/loft/fillet/chamfer,
  single component, small. We approximate "simple" as:
  - 1 or 2 sketches, 1 extrude
  - curves only of {SketchLine, SketchCircle, SketchArc} (no spline/ellipse/conic)
  - <= 8 curves per sketch
  We list how many seqs qualify and give example ids.

Phase1 (Core 300-500): stratified by complexity (Easy/Medium/Hard) defined by
  #sketches & #extrudes & curve complexity.

Phase2 (Stress 100): seqs likely to fail: multi closed profiles, many holes,
  large curve counts (selection ambiguity). Approx: sketches with >= 2 profiles
  (loops) or many circles (holes) or >= 16 curves.

Also verify: does the data encode profiles/loops? (needed to count closed loops)
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

DATASET = Path(r"D:\dataset\r1.0.1\reconstruction")
OUT = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\data\slice_candidates.json")

SIMPLE_CURVES = {"SketchLine", "SketchCircle", "SketchArc"}
COMPLEX_CURVES = {"SketchFittedSpline", "SketchFixedSpline", "SketchEllipse",
                  "SketchEllipticalArc", "SketchConicCurve"}


def main():
    files = sorted(DATASET.glob("*.json"))
    rows = []
    for fp in files:
        d = json.loads(fp.read_text(encoding="utf-8"))
        ents = d.get("entities", {})
        sketches = [e for e in ents.values() if isinstance(e, dict) and e.get("type") == "Sketch"]
        extrudes = [e for e in ents.values() if isinstance(e, dict) and e.get("type") == "ExtrudeFeature"]
        n_sk = len(sketches)
        n_ex = len(extrudes)
        total_curves = sum(len(s.get("curves", {})) for s in sketches)
        curve_types = Counter()
        max_curves_per_sketch = 0
        for s in sketches:
            cv = s.get("curves", {})
            max_curves_per_sketch = max(max_curves_per_sketch, len(cv))
            for c in cv.values():
                if isinstance(c, dict):
                    curve_types[c.get("type", "?")] += 1
        has_complex_curve = any(t in COMPLEX_CURVES for t in curve_types)
        n_circle = curve_types.get("SketchCircle", 0)
        # profile/loop info
        n_profiles = 0
        n_loops = 0
        for s in sketches:
            profs = s.get("profiles", {})
            if isinstance(profs, dict):
                n_profiles += len(profs)
                for p in profs.values():
                    if isinstance(p, dict) and isinstance(p.get("loops"), list):
                        n_loops += len(p["loops"])
        rows.append({
            "id": fp.stem,
            "n_sketch": n_sk,
            "n_extrude": n_ex,
            "total_curves": total_curves,
            "max_curves_per_sketch": max_curves_per_sketch,
            "has_complex_curve": has_complex_curve,
            "n_circle": n_circle,
            "n_profiles": n_profiles,
            "n_loops": n_loops,
            "curve_types": dict(curve_types),
        })

    def classify_phase0(r):
        if r["has_complex_curve"]:
            return False
        if not (1 <= r["n_sketch"] <= 2):
            return False
        if r["n_extrude"] != 1:
            return False
        if r["max_curves_per_sketch"] > 8:
            return False
        return True

    def classify_easy(r):
        return (not r["has_complex_curve"]) and r["n_sketch"] == 1 and r["n_extrude"] == 1 and r["total_curves"] <= 8
    def classify_medium(r):
        if r["has_complex_curve"]:
            return False
        return (r["n_sketch"] in (2, 3)) or (r["n_extrude"] in (2, 3)) or (r["total_curves"] > 8 and r["total_curves"] <= 20)
    def classify_hard(r):
        return r["n_sketch"] >= 4 or r["n_extrude"] >= 4 or r["has_complex_curve"] or r["total_curves"] > 20

    def classify_stress(r):
        return (r["n_loops"] >= 3) or (r["n_circle"] >= 4) or (r["max_curves_per_sketch"] >= 16) or (r["n_profiles"] >= 4)

    phase0 = [r["id"] for r in rows if classify_phase0(r)]
    easy = [r["id"] for r in rows if classify_easy(r)]
    hard = [r["id"] for r in rows if classify_hard(r)]
    medium = [r["id"] for r in rows if classify_medium(r) and not classify_easy(r) and not classify_hard(r)]
    stress = [r["id"] for r in rows if classify_stress(r)]

    # complex curve breakdown
    complex_curve_seq_count = sum(1 for r in rows if r["has_complex_curve"])

    out = {
        "total_seqs": len(rows),
        "phase0_candidates": len(phase0),
        "phase0_examples": phase0[:20],
        "phase1_easy_candidates": len(easy),
        "phase1_medium_candidates": len(medium),
        "phase1_hard_candidates": len(hard),
        "phase2_stress_candidates": len(stress),
        "phase2_stress_examples": stress[:15],
        "seqs_with_complex_curve_spline_etc": complex_curve_seq_count,
        "max_curves_per_sketch_distribution": dict(Counter(r["max_curves_per_sketch"] for r in rows).most_common(20)),
        "profiles_loops_present_seq_count": sum(1 for r in rows if r["n_profiles"] > 0),
        "n_profiles_distribution": dict(Counter(r["n_profiles"] for r in rows).most_common(20)),
        "n_loops_distribution": dict(Counter(r["n_loops"] for r in rows).most_common(20)),
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
