"""Scan ALL 8625 reconstruction JSON files to quantify modality coverage.

Produces stats needed for the data check report:
- top-level keys coverage (how many seqs have metadata/timeline/entities/properties/sequence)
- entity type distribution (Sketch / ExtrudeFeature / Revolve / Fillet / Hole / ...)
- constraint type distribution (the Solver feedback signal source)
- dimension type distribution
- curve type distribution (does it contain splines? -> excludes from Phase0)
- feature operation distribution (NewBody/Cut/Join/Intersect)
- properties key coverage (Kernel Query targets: body_count, volume, etc.)
- per-sequence complexity: #sketches, #extrudes, #curves, #constraints, #fully_constrained ratio
- JSON parse error / structural anomalies

This is read-only and deterministic. Output is printed + saved as JSON.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

DATASET = Path(r"D:\dataset\r1.0.1\reconstruction")
OUT = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\data\scan_stats.json")


def main():
    toplevel = Counter()
    entity_types = Counter()
    constraint_types = Counter()
    dimension_types = Counter()
    curve_types = Counter()
    feature_ops = Counter()  # extrude/revolve operation
    feature_extent_types = Counter()
    properties_keys = Counter()
    surface_types = Counter()

    # per-seq complexity distributions
    n_sketch = Counter()
    n_extrude = Counter()
    n_other_feat = Counter()
    n_curves = Counter()
    n_constraints = Counter()
    n_dimensions = Counter()
    fully_constrained_ratios = []  # per sketch

    parse_errors = []
    seq_roots = []

    files = sorted(DATASET.glob("*.json"))
    print(f"scanning {len(files)} json files ...")
    for i, fp in enumerate(files):
        seq_roots.append(fp.stem)
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            parse_errors.append((fp.name, str(e)))
            continue
        if not isinstance(d, dict):
            parse_errors.append((fp.name, "not a dict"))
            continue
        for k in d.keys():
            toplevel[k] += 1

        ents = d.get("entities")
        if not isinstance(ents, dict):
            continue

        seq_sketches = 0
        seq_extrudes = 0
        seq_other = 0
        for uuid, e in ents.items():
            if not isinstance(e, dict):
                continue
            et = e.get("type", "?")
            entity_types[et] += 1
            if et == "Sketch":
                seq_sketches += 1
                curves = e.get("curves", {})
                if isinstance(curves, dict):
                    n_curves[len(curves)] += 1
                    fc_true = sum(1 for c in curves.values()
                                  if isinstance(c, dict) and c.get("fully_constrained"))
                    if curves:
                        fully_constrained_ratios.append(fc_true / len(curves))
                    for c in curves.values():
                        if isinstance(c, dict):
                            curve_types[c.get("type", "?")] += 1
                cons = e.get("constraints", {})
                if isinstance(cons, dict):
                    n_constraints[len(cons)] += 1
                    for c in cons.values():
                        if isinstance(c, dict):
                            constraint_types[c.get("type", "?")] += 1
                dims = e.get("dimensions", {})
                if isinstance(dims, dict):
                    n_dimensions[len(dims)] += 1
                    for dd in dims.values():
                        if isinstance(dd, dict):
                            dimension_types[dd.get("type", "?")] += 1
            elif et == "ExtrudeFeature":
                seq_extrudes += 1
                feature_ops[e.get("operation", "?")] += 1
                feature_extent_types[e.get("extent_type", "?")] += 1
            else:
                seq_other += 1
                # capture face surface types for any feature
        n_sketch[seq_sketches] += 1
        n_extrude[seq_extrudes] += 1
        n_other_feat[seq_other] += 1

        props = d.get("properties")
        if isinstance(props, dict):
            for k in props.keys():
                properties_keys[k] += 1

        if i % 1000 == 0 and i > 0:
            print(f"  ... {i}/{len(files)}")

    # global surface types from a quick second sweep is expensive; skip (already plenty)
    import statistics

    def top(c, n=20):
        return c.most_common(n)

    fc_mean = statistics.mean(fully_constrained_ratios) if fully_constrained_ratios else 0
    fc_median = statistics.median(fully_constrained_ratios) if fully_constrained_ratios else 0

    stats = {
        "total_json": len(files),
        "parse_errors": len(parse_errors),
        "parse_error_examples": parse_errors[:10],
        "toplevel_key_counts": dict(toplevel),
        "entity_types": top(entity_types, 30),
        "constraint_types": top(constraint_types, 30),
        "dimension_types": top(dimension_types, 30),
        "curve_types": top(curve_types, 30),
        "feature_operations": top(feature_ops, 20),
        "feature_extent_types": top(feature_extent_types, 20),
        "properties_key_coverage": top(properties_keys, 30),
        "per_seq_sketch_count_dist": top(n_sketch, 15),
        "per_seq_extrude_count_dist": top(n_extrude, 15),
        "per_seq_other_feature_count_dist": top(n_other_feat, 15),
        "per_seq_curve_count_dist": top(n_curves, 15),
        "per_seq_constraint_count_dist": top(n_constraints, 15),
        "per_seq_dimension_count_dist": top(n_dimensions, 15),
        "fully_constrained_ratio_mean": round(fc_mean, 4),
        "fully_constrained_ratio_median": round(fc_median, 4),
        "n_sketches_with_fully_constrained_data": len(fully_constrained_ratios),
    }
    OUT.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== SUMMARY (saved to", OUT.name, ") ===")
    print(json.dumps({k: v for k, v in stats.items() if not isinstance(v, list) or k.endswith("dist") or "types" in k or "coverage" in k}, indent=2, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
