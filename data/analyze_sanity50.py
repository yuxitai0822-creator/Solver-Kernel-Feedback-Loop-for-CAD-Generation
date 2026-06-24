"""Deep structural analysis of the 50 sanity-set modeling sequences.

Goal: feed the design of the deterministic KQP compiler. We extract, for every
of the 50 samples:
- timeline structure (operation ordering, entity refs)
- entity inventory (sketch / extrude field schemas, with all keys observed)
- sketch sub-structure: points / curves / constraints / dimensions / profiles
- extrude sub-structure: profiles, operation, extent_type, extent distance,
  start_extent, reference planes, target bodies
- the dependency graph: which extrude consumes which sketch's which profile
- where each numeric value lives (so KQP knows where to pull expected numbers)

Outputs a human-readable text dump + a compact JSON summary used by the report.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

SET = Path(__file__).resolve().parent / "sanity_set_50"
OUT_TXT = Path(__file__).resolve().parent / "sanity50_structure_dump.txt"
OUT_JSON = Path(__file__).resolve().parent / "sanity50_structure.json"


def schema_of(obj, depth=0, maxd=4):
    """Return a compact type-shape signature of a nested json object."""
    if depth > maxd:
        return "..."
    if isinstance(obj, dict):
        return {k: schema_of(v, depth + 1, maxd) for k, v in list(obj.items())[:30]}
    if isinstance(obj, list):
        if not obj:
            return []
        return [schema_of(obj[0], depth + 1, maxd), f"<len varies>"]
    return type(obj).__name__


def main():
    jsons = sorted(SET.glob("*.json"))
    lines = []
    summary = {
        "n_samples": len(jsons),
        "all_timeline_keys": Counter(),
        "all_sketch_keys": Counter(),
        "all_extrude_keys": Counter(),
        "curve_types": Counter(),
        "constraint_types": Counter(),
        "dimension_types": Counter(),
        "extent_types": Counter(),
        "operations": Counter(),
        "extent_one_keys": Counter(),
        "start_extent_keys": Counter(),
        "sketch_plane_keys": Counter(),
        "profile_keys": Counter(),
        "loop_keys": Counter(),
        "point_keys": Counter(),
        "param_keys": Counter(),
        "n_sketches_dist": Counter(),
        "n_extrudes_dist": Counter(),
        "n_profiles_dist": Counter(),
        "n_loops_dist": Counter(),
        "n_curves_dist": Counter(),
        "per_sample": [],
    }

    for fp in jsons:
        d = json.loads(fp.read_text(encoding="utf-8"))
        ents = d.get("entities", {})
        timeline = d.get("timeline", [])
        metadata = d.get("metadata", {})

        sketches = [(u, e) for u, e in ents.items() if isinstance(e, dict) and e.get("type") == "Sketch"]
        extrudes = [(u, e) for u, e in ents.items() if isinstance(e, dict) and e.get("type") == "ExtrudeFeature"]

        sample = {"id": fp.stem, "design": metadata.get("parent_project"),
                  "n_sketch": len(sketches), "n_extrude": len(extrudes),
                  "sketches": [], "extrudes": [], "timeline_len": len(timeline)}
        summary["n_sketches_dist"][len(sketches)] += 1
        summary["n_extrudes_dist"][len(extrudes)] += 1

        # timeline keys
        for t in timeline:
            if isinstance(t, dict):
                for k in t.keys():
                    summary["all_timeline_keys"][k] += 1

        for uuid, s in sketches:
            for k in s.keys():
                summary["all_sketch_keys"][k] += 1
            curves = s.get("curves", {})
            cons = s.get("constraints", {})
            dims = s.get("dimensions", {})
            pts = s.get("points", {})
            profs = s.get("profiles", {})
            plane = s.get("plane", s.get("reference_plane", {}))
            summary["n_curves_dist"][len(curves)] += 1
            summary["n_profiles_dist"][len(profs)] += 1
            for c in curves.values():
                if isinstance(c, dict):
                    summary["curve_types"][c.get("type", "?")] += 1
            for c in cons.values():
                if isinstance(c, dict):
                    summary["constraint_types"][c.get("type", "?")] += 1
            for dd in dims.values():
                if isinstance(dd, dict):
                    summary["dimension_types"][dd.get("type", "?")] += 1
                    param = dd.get("parameter", {})
                    if isinstance(param, dict):
                        for pk in param.keys():
                            summary["param_keys"][pk] += 1
            for p in pts.values():
                if isinstance(p, dict):
                    for pk in p.keys():
                        summary["point_keys"][pk] += 1
            for p in profs.values():
                if isinstance(p, dict):
                    for pk in p.keys():
                        summary["profile_keys"][pk] += 1
                    loops = p.get("loops", [])
                    summary["n_loops_dist"][len(loops)] += 1
                    for lp in loops:
                        if isinstance(lp, dict):
                            for lk in lp.keys():
                                summary["loop_keys"][lk] += 1
            if isinstance(plane, dict):
                for pk in plane.keys():
                    summary["sketch_plane_keys"][pk] += 1

            sample["sketches"].append({
                "uuid": uuid,
                "curve_types": dict(Counter(c.get("type") for c in curves.values() if isinstance(c, dict))),
                "n_curves": len(curves), "n_constraints": len(cons),
                "n_dimensions": len(dims), "n_points": len(pts), "n_profiles": len(profs),
                "plane": schema_of(plane, maxd=2),
                "sample_curve": schema_of(next(iter(curves.values())) if curves else {}, maxd=3),
                "sample_constraint": schema_of(next(iter(cons.values())) if cons else {}, maxd=3),
                "sample_dimension": schema_of(next(iter(dims.values())) if dims else {}, maxd=4),
                "sample_point": schema_of(next(iter(pts.values())) if pts else {}, maxd=2),
                "sample_profile": schema_of(next(iter(profs.values())) if profs else {}, maxd=4),
            })

        for uuid, e in extrudes:
            for k in e.keys():
                summary["all_extrude_keys"][k] += 1
            summary["operations"][e.get("operation", "?")] += 1
            summary["extent_types"][e.get("extent_type", "?")] += 1
            e1 = e.get("extent_one", {})
            se = e.get("start_extent", {})
            if isinstance(e1, dict):
                for k in e1.keys():
                    summary["extent_one_keys"][k] += 1
            if isinstance(se, dict):
                for k in se.keys():
                    summary["start_extent_keys"][k] += 1
            sample["extrudes"].append({
                "uuid": uuid,
                "operation": e.get("operation"),
                "extent_type": e.get("extent_type"),
                "profile_refs": e.get("profiles"),
                "extent_one": schema_of(e1, maxd=3),
                "start_extent": schema_of(se, maxd=3),
                "all_keys": list(e.keys()),
            })
        summary["per_sample"].append(sample)

    # write compact JSON summary
    def to_dict(c):
        return {k: v for k, v in c.most_common()} if isinstance(c, Counter) else c
    OUT_JSON.write_text(json.dumps({k: to_dict(v) for k, v in summary.items()},
                                   indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    # write human-readable dump
    L = lines.append
    L("=" * 70)
    L("SANITY SET (50) — MODELING SEQUENCE STRUCTURE DUMP")
    L("=" * 70)
    L(f"samples: {summary['n_samples']}")
    L("")

    def block(title, c, topn=30):
        L(f"--- {title} ---")
        for k, v in c.most_common(topn):
            L(f"  {k}: {v}")
        L("")

    L("GLOBAL DISTRIBUTIONS")
    block("all timeline keys", summary["all_timeline_keys"])
    block("all sketch keys", summary["all_sketch_keys"])
    block("all extrude keys", summary["all_extrude_keys"])
    block("curve types", summary["curve_types"])
    block("constraint types", summary["constraint_types"])
    block("dimension types", summary["dimension_types"])
    block("operations (extrude op)", summary["operations"])
    block("extent types", summary["extent_types"])
    block("extent_one keys", summary["extent_one_keys"])
    block("start_extent keys", summary["start_extent_keys"])
    block("sketch plane keys", summary["sketch_plane_keys"])
    block("profile keys", summary["profile_keys"])
    block("loop keys", summary["loop_keys"])
    block("point keys", summary["point_keys"])
    block("parameter keys (inside dimensions)", summary["param_keys"])
    block("n_sketches per sample", summary["n_sketches_dist"])
    block("n_extrudes per sample", summary["n_extrudes_dist"])
    block("n_curves per sketch", summary["n_curves_dist"])
    block("n_profiles per sketch", summary["n_profiles_dist"])
    block("n_loops per profile", summary["n_loops_dist"])

    L("=" * 70)
    L("PER-SAMPLE DETAIL (first 5 shown fully)")
    L("=" * 70)
    for s in summary["per_sample"][:5]:
        L(json.dumps(s, indent=2, ensure_ascii=False, default=str))
        L("")

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON.name} and {OUT_TXT.name}")
    print("\nKEY DISTRIBUTIONS PREVIEW")
    for name in ["curve_types", "constraint_types", "dimension_types", "operations", "extent_types"]:
        c = summary[name]
        print(f"  {name}: {dict(c.most_common())}")


if __name__ == "__main__":
    main()
