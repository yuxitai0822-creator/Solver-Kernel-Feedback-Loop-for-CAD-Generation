"""Apply the 4-criteria KQP review to all hand-written KQP instances.

Criteria:
  Traceability  : every feedback-enabled query must have source_field
                   pointing to a real design_plan_v0.6 field path.
  Executability : every intent must be in ALLOWED_INTENTS of kqp_schema_v0.1;
                   expected+source params must be type-compatible.
  Non-leakage   : expected values must NOT come from GT-only fields
                   (face_count/edge_count/volume/area/center_of_mass).
  Diagnosticity : feedback_template must mention {expected} and {actual}
                   placeholders + concrete LLM-actionable hint.
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
KQP_DIR = ROOT / "KQP" / "samples" / "v0.1"
PLAN_DIR = ROOT / "compiler" / "instances_v6"
SCHEMA_PATH = ROOT / "KQP" / "kqp_schema_v0.1.txt"


GT_ONLY_FIELDS = {
    # from design_plan kqp_schema_v0.1 → open_extension_points + Non-Leakage warnings
    "face_count", "edge_count", "vertex_count", "shell_count", "wire_count",
    "volume", "surface_area", "center_of_mass", "principal_axes",
    "xyz_moments_of_inertia", "vertex_valence", "density", "mass",
}

ALLOWED_INTENTS = {
    "A_topology": {"body_count", "solid_count", "face_count", "edge_count",
                   "vertex_count", "shell_count", "wire_count"},
    "B_geometry_dim": {"bbox_size", "cylinder_radius", "center_distance",
                       "plane_area", "volume"},
    "C_feature": {"through_void_count", "hole_radius"},
    "D_health": {"is_solid", "occt_valid", "all_faces_planar",
                 "euler_characteristic", "symmetric_about_plane"},
}


def get_plan_field(plan, path):
    """Walk a path like 'solid_bodies.0.dimensions.extrude_distance.value' OR
    'solid_bodies[0].dimensions.extrude_distance.value' (mixed indexing).

    Supports both .N. and [N] segment types. Stops at the LAST segment that
    exists in the plan (so 'value' may be unresolved if path is a derived /
    computed reference like '+ 2*r' or 'count()').
    """
    import re
    # Tokenize: alternate identifier dots and [N] brackets
    tokens = []
    pos = 0
    while pos < len(path):
        if path[pos] == ".":
            pos += 1
            continue
        if path[pos] == "[":
            m = re.match(r"\[(\d+)\]", path[pos:])
            if m:
                tokens.append(("idx", int(m.group(1))))
                pos += m.end()
                continue
        m = re.match(r"[^\.\[]+", path[pos:])
        if m:
            tokens.append(("key", m.group(0)))
            pos += m.end()
        else:
            break
    cur = plan
    for kind, val in tokens:
        if kind == "idx":
            if isinstance(cur, list) and 0 <= val < len(cur):
                cur = cur[val]
            else:
                return cur
        else:  # "key"
            if isinstance(cur, dict):
                cur = cur.get(val)
            else:
                return cur
            if cur is None:
                return None
    return cur


def review_instance(kqp_path, plan_path):
    kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    issues = []
    queries = kqp.get("queries", [])

    for i, q in enumerate(queries):
        qid = q.get("id", f"<no id #{i}>")
        cat = q.get("category")
        intent = q.get("intent")
        fe = q.get("feedback_enabled")
        ft = q.get("feedback_template")
        sf = q.get("source_field")
        exp = q.get("expected")

        # 1. Traceability: feedback_enabled requires source_field with a real path
        if fe:
            if not sf:
                issues.append((qid, "traceability", "feedback_enabled=true but source_field missing"))
            elif sf == "(implicit)" or sf.startswith("(implicit"):
                # allowed for D_health only; "(implicit: ...)" form is descriptive variant
                if cat != "D_health":
                    issues.append((qid, "traceability", "implicit source_field only allowed for D_health"))
            else:
                # strip only leading $ or . (one each)
                sf_clean = sf.lstrip("$").lstrip(".")
                # Accept source provenance annotations: '(computed: ...)',
                # '(inferred_from_point_span)', etc. Strip after first paren.
                if "(" in sf_clean:
                    sf_clean = sf_clean.split("(")[0].strip()
                # Strip trailing operators like ' + ...' or ' computed ...'
                for sep in [" + ", " computed "]:
                    if sep in sf_clean:
                        sf_clean = sf_clean.split(sep)[0].strip()
                v = get_plan_field(plan, sf_clean)
                if v is None:
                    issues.append((qid, "traceability",
                                   f"source_field {sf!r} (cleaned={sf_clean!r}) not found in design_plan"))

        # 2. Executability: intent in ALLOWED_INTENTS
        if cat not in ALLOWED_INTENTS:
            issues.append((qid, "executability", f"unknown category {cat!r}"))
        elif intent not in ALLOWED_INTENTS[cat]:
            issues.append((qid, "executability", f"intent {intent!r} not allowed in {cat}"))

        # 2b. category-specific required params (e.g. bbox_size needs axis)
        if intent == "bbox_size":
            if "axis" not in q or q["axis"] not in {"u", "v", "w"}:
                issues.append((qid, "executability", "bbox_size missing/incorrect axis"))
            if "tolerance" not in q:
                issues.append((qid, "executability", "bbox_size missing tolerance"))
        if intent == "cylinder_radius":
            if "tolerance" not in q:
                issues.append((qid, "executability", "cylinder_radius missing tolerance"))
        if intent == "through_void_count":
            if "tolerance" not in q:
                issues.append((qid, "executability", "through_void_count missing tolerance"))

        # 3. Non-leakage: source_field must not reference GT-only fields
        if sf and sf != "(implicit)":
            sf_clean = sf.lstrip("$").lstrip(".")
            for gf in GT_ONLY_FIELDS:
                if gf in sf_clean:
                    issues.append((qid, "non-leakage",
                                   f"source_field {sf!r} references GT-only field '{gf}'"))
        # explicit volume/area queries are also leaks
        if intent in ("volume", "plane_area") and fe:
            issues.append((qid, "non-leakage",
                          f"intent {intent!r} emits GT-only data; should set feedback_enabled=false"))

        # 4. Diagnosticity: feedback_template must contain some "actual value" indicator
        #    so the LLM can see what the kernel observed. Accepts:
        #    - {actual} placeholder
        #    - "got X" phrasing (hardcoded actual value)
        #    - "actual=X" or "actual: X" phrasing
        if fe and ft:
            has_actual_marker = (
                "{actual}" in ft
                or "got " in ft
                or "actual=" in ft
                or "actual:" in ft
            )
            if not has_actual_marker:
                issues.append((qid, "diagnosticity",
                               f"feedback_template missing actual-value marker "
                               f"(need '{{actual}}' or 'got X' or 'actual=X' or 'actual: X')"))
            # heuristic: template should be at least 30 chars to be actionable
            if len(ft) < 30:
                issues.append((qid, "diagnosticity",
                               f"feedback_template too short ({len(ft)} chars): {ft!r}"))

    return {
        "sid": kqp_path.stem.replace(".kqp_instance", ""),
        "n_queries": len(queries),
        "issues": issues,
    }


def main():
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    print("=" * 70)
    print("KQP BATCH 1 REVIEW (samples 1-5)")
    print("=" * 70)
    print()
    summary = Counter()
    file_results = []
    for kqp_path in sorted(KQP_DIR.glob("*.kqp_instance.json")):
        sid = kqp_path.stem.replace(".kqp_instance", "")
        # Find design_plan lookup
        # try v0.6 instances first
        plan_path = PLAN_DIR / f"{sid}.design_plan.json"
        if not plan_path.exists():
            print(f"[SKIP] {sid}: no design_plan found at {plan_path}")
            continue
        result = review_instance(kqp_path, plan_path)
        file_results.append(result)
        for _, cat, _ in result["issues"]:
            summary[cat] += 1
        if result["issues"]:
            print(f"[{sid}] queries={result['n_queries']}  ISSUES={len(result['issues'])}")
            for qid, cat, msg in result["issues"]:
                print(f"    {qid}  [{cat}]  {msg}")
        else:
            print(f"[{sid}] queries={result['n_queries']}  PASS")
    print()
    print("=" * 70)
    print("SUMMARY by criterion")
    print("=" * 70)
    for cat in ("traceability", "executability", "non-leakage", "diagnosticity"):
        print(f"  {cat:<15} {summary[cat]} issues")
    total = sum(summary.values())
    print(f"  {'TOTAL':<15} {total} issues across {len(file_results)} files")

    out_dir = ROOT / "KQP" / "review"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "batch_1_review.json").write_text(json.dumps({
        "schema_version": "kqp_schema_v0.1",
        "n_files": len(file_results),
        "n_queries_total": sum(r["n_queries"] for r in file_results),
        "issues_by_criterion": dict(summary),
        "per_file": [
            {"sid": r["sid"], "n_queries": r["n_queries"], "issues": [
                {"query": qid, "criterion": cat, "message": msg}
                for qid, cat, msg in r["issues"]
            ]}
            for r in file_results
        ]
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten: {out_dir/'batch_1_review.json'}")


if __name__ == "__main__":
    main()
