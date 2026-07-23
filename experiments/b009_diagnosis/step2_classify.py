"""Step 2 of the B-009 diagnosis (read-only):
- For each regressed query, apply the decision tree to classify as
  (I) direction mismatch, (II) value misassignment, or (III) impl bug.

Output: experiments/b009_diagnosis/regression_classification.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "experiments/b009_diagnosis/regressed_samples.json").read_text(encoding="utf-8"))
OUT = ROOT / "experiments/b009_diagnosis" / "regression_classification.json"


def classify_query(q: dict) -> dict:
    E = q["expected"]
    F = q["frame_axis_span"]
    world_spans = q["world_spans"]
    tol = max(q["tolerance"] * 50, 1.0)

    # Question A: frame_axis_span ≈ expected?
    if abs(F - E) <= tol:
        # Frame-axis matched expected. Should not have regressed.
        # → Class (III) implementation bug.
        return {
            "class": "III",
            "evidence": (f"frame_axis_span={F:.4f} ≈ expected={E:.4f} within "
                            f"tolerance {tol:.4f}, but query still regressed — "
                            f"the frame-axis implementation itself has a bug."),
            "permutation": None,
            "bestmatch_axis": q.get("bestmatch_axis"),
            "bestmatch_span": q.get("bestmatch_span"),
        }
    # Question B: some other world axis span ≈ expected?
    matches = []
    for ax, ws in world_spans.items():
        if abs(ws - E) <= tol:
            matches.append((ax, ws))
    if matches:
        # body HAS the expected dim, just not along frame.u_dir → (I)
        # Record which world axis the body actually has, vs what
        # the frame says.
        match_axes = [m[0] for m in matches]
        match_vals = [m[1] for m in matches]
        return {
            "class": "I",
            "evidence": (f"frame_axis_span={F:.4f} ≠ expected={E:.4f}; "
                            f"world axis(es) {match_axes} with span(s) {match_vals} "
                            f"match the expected, indicating the body is "
                            f"rotated relative to the design plan's frame "
                            f"({q['frame_dir']})."),
            "permutation": q["frame_axis"] + "→" + match_axes[0],
            "bestmatch_axis": q.get("bestmatch_axis"),
            "bestmatch_span": q.get("bestmatch_span"),
        }
    # Question C: no world axis matches
    # expected value doesn't match ANY world span of the body
    return {
        "class": "II",
        "evidence": (f"frame_axis_span={F:.4f} ≠ expected={E:.4f}; "
                        f"no world axis span (X={world_spans['x']:.4f}, "
                        f"Y={world_spans['y']:.4f}, Z={world_spans['z']:.4f}) "
                        f"matches expected {E:.4f}. The expected value is not "
                        f"realised by the body — a value-misassignment in "
                        f"the design plan or history."),
        "permutation": None,
        "bestmatch_axis": q.get("bestmatch_axis"),
        "bestmatch_span": q.get("bestmatch_span"),
    }


def main():
    classification = {"I": [], "II": [], "III": []}
    sample_summary = []
    for r in data["regressed_samples"]:
        sid = r["sample_id"]
        classifications = []
        for q in r["regressed_queries"]:
            c = classify_query(q)
            classifications.append({
                "query_id": q["query_id"],
                "expected": q["expected"],
                "frame_axis": q["frame_axis"],
                "class": c["class"],
                "permutation": c["permutation"],
                "evidence": c["evidence"],
            })
            classification[c["class"]].append({
                "sample_id": sid,
                "query_id": q["query_id"],
                "expected": q["expected"],
                "frame_dir": q["frame_dir"],
                "frame_axis_span": q["frame_axis_span"],
                "world_spans": q["world_spans"],
            })
        sample_summary.append({
            "sample_id": sid,
            "n_regressed": len(classifications),
            "classifications": classifications,
        })
    out = {
        "n_regressed_samples": len(sample_summary),
        "n_class_I": len(classification["I"]),
        "n_class_II": len(classification["II"]),
        "n_class_III": len(classification["III"]),
        "per_sample": sample_summary,
        "by_class": classification,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"  Class I (direction mismatch): {len(classification['I'])} queries")
    print(f"  Class II (value misassignment): {len(classification['II'])} queries")
    print(f"  Class III (impl bug): {len(classification['III'])} queries")
    print()
    if classification["III"]:
        print("⚠️  Class III samples (frame-axis projection may have a bug):")
        for q in classification["III"][:5]:
            print(f"  - {q['sample_id']} / {q['query_id']}: {q['evidence']}")
    if classification["II"]:
        print("\nClass II samples (DP value misassignment):")
        for q in classification["II"][:5]:
            print(f"  - {q['sample_id']} / {q['query_id']}: {q['evidence']}")


if __name__ == "__main__":
    main()
