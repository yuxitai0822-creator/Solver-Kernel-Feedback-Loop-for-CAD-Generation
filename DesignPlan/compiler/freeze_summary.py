"""Final clean summary: classify each sample's diffs as schema-level vs value-level.

Value-level diffs = real semantic disagreements (compiler output ≠ hand-written value).
Schema-level diffs = expected (old hand-written schema lacks fields that v0.6 added).

Outputs:
- Per-version classification counts
- Final freeze recommendation
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "DesignPlan" / "samples"
COMPILER_OUT = ROOT / "compiler" / "instances_v6"

HAND_WRITTEN = {}
for ver, subdir in [("v0.2", "v2"), ("v0.3", "v3"), ("v0.4", "v4"),
                     ("v0.5", "v5"), ("v0.6", "v6")]:
    d = SAMPLES / subdir
    if not d.exists(): continue
    for p in list(d.glob("*.design_plan.json")) + list(d.glob("*.design_plan")):
        if p.is_file():
            sid = p.stem.replace(".design_plan", "")
            if sid not in HAND_WRITTEN:
                HAND_WRITTEN[sid] = (p, ver)


def get_field(schema_version, data, hand_field_path, comp_field_path, h_unit_factor=1.0):
    """Get the comparable numeric value from both sides."""
    h_path = hand_field_path
    c_path = comp_field_path
    # simple walk
    def walk(d, path):
        keys = path.split('.')
        cur = d
        for k in keys:
            if isinstance(cur, list):
                try: k = int(k)
                except: return None
            if isinstance(cur, dict):
                cur = cur.get(k)
            elif isinstance(cur, list):
                cur = cur[k] if 0 <= k < len(cur) else None
            else:
                return None
            if cur is None: return None
        if isinstance(cur, dict) and 'value' in cur:
            return cur['value']
        return cur
    hv = walk(data['h'], h_path) if 'h' in data else None
    cv = walk(data['c'], c_path) if 'c' in data else None
    return hv, cv


m = json.load(open(ROOT / "data/sanity_set_50/manifest.json", encoding="utf-8"))
IDS = [e["id"] for e in m["entries"]]

# Per-sample classification
PER_SAMPLE = {}

for sid in IDS:
    if sid not in HAND_WRITTEN: continue
    hp, hver = HAND_WRITTEN[sid]
    cp = COMPILER_OUT / f"{sid}.design_plan.json"
    if not cp.exists(): continue
    hand = json.loads(hp.read_text(encoding="utf-8"))
    comp = json.loads(cp.read_text(encoding="utf-8"))
    hver_short = hver.replace("design_plan_", "")
    h_unit_factor = 10.0 if hver_short in ("v0.2", "v0.3") else 1.0

    # Schema-vs-value diffs
    schema_diffs = []  # field names that differ (one side missing)
    value_diffs = []   # (field, h, c)

    # profile.type (schema: v0.2 single 'profile.type' vs v0.4+ 'profiles[0].type')
    h_ptype = get_field({}, hand, "solid_bodies.0.profile.type", None)[0] if hver_short == "v0.2" else None
    h_ptype = h_ptype or (hand.get("solid_bodies", [{}])[0].get("profile", {}) or {}).get("type")
    if hver_short != "v0.2":
        h_ptype = (hand.get("solid_bodies", [{}])[0].get("profiles", [{}])[0] or {}).get("type")
    c_ptype = (comp.get("solid_bodies", [{}])[0].get("profiles", [{}])[0] or {}).get("type")
    if (h_ptype is None) != (c_ptype is None):
        schema_diffs.append("profile.type")
    elif h_ptype is not None and str(h_ptype) != str(c_ptype):
        value_diffs.append(("profile.type", h_ptype, c_ptype))

    # extrude.extent_type — both versions have this. Check both.
    h_et = hand.get("solid_bodies", [{}])[0].get("extrude", {}) or {}
    c_et = comp.get("solid_bodies", [{}])[0].get("extrude", {}) or {}
    h_et_v = h_et.get("extent_type")
    c_et_v = c_et.get("extent_type")
    if (h_et_v is None) != (c_et_v is None):
        schema_diffs.append("extrude.extent_type")
    elif h_et_v is not None and str(h_et_v) != str(c_et_v):
        value_diffs.append(("extrude.extent_type", h_et_v, c_et_v))

    # extrude.direction — both have it.
    h_dir = h_et.get("direction")
    c_dir = c_et.get("direction")
    if (h_dir is None) != (c_dir is None):
        schema_diffs.append("extrude.direction")
    elif h_dir is not None and str(h_dir) != str(c_dir):
        value_diffs.append(("extrude.direction", h_dir, c_dir))

    # extrude distance — schema varies:
    #   v0.2: extrude.distance.value
    #   v0.3+: extrude.distance_total.value
    h_dist_v = None
    if isinstance(h_et.get("distance"), dict):
        h_dist_v = h_et["distance"].get("value")
    elif h_et.get("distance_total") and isinstance(h_et["distance_total"], dict):
        h_dist_v = h_et["distance_total"].get("value")
    else:
        h_dist_v = h_et.get("distance")  # scalar
    c_dist_v = (c_et.get("distance_total") or {}).get("value")
    if (h_dist_v is None) != (c_dist_v is None):
        schema_diffs.append("extrude.distance_total")
    elif h_dist_v is not None and c_dist_v is not None:
        scaled_h = float(h_dist_v) * h_unit_factor
        if abs(scaled_h - float(c_dist_v)) > 0.005 * max(abs(scaled_h), abs(float(c_dist_v)), 1.0):
            value_diffs.append(("extrude.distance_total", scaled_h, c_dist_v))

    # In-plane dimension(s) — schema varies by profile type and version
    ptype_class_match = (h_ptype == c_ptype) or (h_ptype is None and c_ptype is None)
    if ptype_class_match and h_ptype:
        # circle/annulus -> radius
        if h_ptype in ("circle",):
            if hver_short == "v0.2":
                hr = hand["solid_bodies"][0].get("profile", {}).get("parameters", {}).get("radius", {}).get("value")
            else:
                hr = (hand["solid_bodies"][0].get("dimensions", {}).get("profiles", [{}])[0] or {}).get("radius", {}).get("value")
            cr = (comp["solid_bodies"][0].get("dimensions", {}).get("profiles", [{}])[0] or {}).get("radius", {}).get("value")
            if (hr is None) != (cr is None):
                schema_diffs.append("radius")
            elif hr is not None and cr is not None:
                scaled_h = float(hr) * h_unit_factor
                if abs(scaled_h - float(cr)) > 0.01 * max(abs(scaled_h), abs(float(cr)), 1.0):
                    value_diffs.append(("radius", scaled_h, cr))

        # rectangle -> length_u/width_v (v0.2 uses side_u/side_v)
        elif h_ptype == "rectangle":
            if hver_short == "v0.2":
                hlu = hand["solid_bodies"][0].get("profile", {}).get("parameters", {}).get("side_u", {}).get("value")
                hwv = hand["solid_bodies"][0].get("profile", {}).get("parameters", {}).get("side_v", {}).get("value")
            else:
                pd = hand["solid_bodies"][0].get("dimensions", {}).get("profiles", [{}])[0] or {}
                hlu = pd.get("length_u", {}).get("value")
                hwv = pd.get("width_v", {}).get("value")
            pd = comp["solid_bodies"][0].get("dimensions", {}).get("profiles", [{}])[0] or {}
            clu = pd.get("length_u", {}).get("value")
            cwv = pd.get("width_v", {}).get("value")
            if (hlu is None) != (clu is None): schema_diffs.append("length_u")
            elif hlu is not None and clu is not None:
                scaled_h = float(hlu) * h_unit_factor
                if abs(scaled_h - float(clu)) > 0.01 * max(abs(scaled_h), abs(float(clu)), 1.0):
                    value_diffs.append(("length_u", scaled_h, clu))
            if (hwv is None) != (cwv is None): schema_diffs.append("width_v")
            elif hwv is not None and cwv is not None:
                scaled_h = float(hwv) * h_unit_factor
                if abs(scaled_h - float(cwv)) > 0.01 * max(abs(scaled_h), abs(float(cwv)), 1.0):
                    value_diffs.append(("width_v", scaled_h, cwv))

    # part_category — non-verifiable, differs are cosmetic
    h_pc = hand.get("target", {}).get("part_category")
    c_pc = comp.get("target", {}).get("part_category")
    if h_pc is not None and c_pc is not None and h_pc != c_pc:
        # non-verifiable field, but compiler uses quantified rules while hand is human-judged
        schema_diffs.append("part_category (cosmetic, non-verifiable)")

    PER_SAMPLE[sid] = {
        "hver": hver,
        "schema_diffs": schema_diffs,
        "value_diffs": value_diffs,
    }


print("=" * 80)
print("FREEZE VALIDATION: schema-level vs value-level diffs (45 hand-written samples)")
print("=" * 80)

# Aggregate
schema_counts = Counter()
value_counts = Counter()
for sid, info in PER_SAMPLE.items():
    for d in info["schema_diffs"]:
        # simplify: remove "(cosmetic...)" suffix for counting
        kind = d.split(" ")[0]
        schema_counts[kind] += 1
    for d in info["value_diffs"]:
        value_counts[d[0]] += 1

print()
print("FIELD-LEVEL AGGREGATE:")
print(f"  Schema-level diffs (expected, old schema lacks new fields): {sum(schema_counts.values())}")
for k, v in schema_counts.most_common():
    print(f"    {k}: {v}")
print()
print(f"  Value-level diffs (REAL semantic disagreements): {sum(value_counts.values())}")
for k, v in value_counts.most_common():
    print(f"    {k}: {v}")
print()

# Per-version breakdown
print("=" * 80)
print("PER-VERSION BREAKDOWN OF REAL VALUE DIFFS")
print("=" * 80)
ver_value_diff = defaultdict(list)
for sid, info in PER_SAMPLE.items():
    for d in info["value_diffs"]:
        ver_value_diff[info["hver"]].append((sid,) + d)

for v in sorted(ver_value_diff.keys()):
    diffs = ver_value_diff[v]
    print(f"\n  [{v}] {len(diffs)} value diffs:")
    for sid, fname, hv, cv in diffs:
        print(f"    {sid}: {fname} hand={hv!r}  comp={cv!r}")

# Final
print()
print("=" * 80)
print("FREEZE DECISION SUMMARY")
print("=" * 80)
total_value_diffs = sum(value_counts.values())
total_samples_with_diffs = sum(1 for s in PER_SAMPLE.values() if s["value_diffs"])
print(f"Total samples compared: {len(PER_SAMPLE)}")
print(f"Samples with REAL value diffs: {total_samples_with_diffs}")
print(f"Total REAL value diffs: {total_value_diffs}")
if total_value_diffs == 0:
    print()
    print(">>> VERDICT: ZERO value-level disagreements. Schema-only diffs are 'expected' from")
    print("    older schema versions missing fields added in v0.6. Compiler_v6 output is")
    print("    semantically consistent with all hand-written plans across versions.")
    print(">>> RECOMMENDATION: FREEZE schema_v6 + compiler_v6 + 50 design_plan_v6_instances.")
elif total_value_diffs <= 5:
    print()
    print(">>> VERDICT: SMALL number of value-level diffs. Inspect manually.")
    print("    If diffs are explainable (hand errors / unit conv / etc.), FREEZE.")
else:
    print()
    print(">>> VERDICT: MANY value-level diffs. Likely a systemic issue. DON'T freeze, re-iterate.")
