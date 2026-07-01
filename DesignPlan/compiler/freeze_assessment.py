"""Freeze assessment: check semantic (numeric) agreement between hand-written
plans at older schema versions vs compiler_v6 output, AFTER compensating
for schema field name changes (singular 'profile' vs plural 'profiles[]'
between v0.2 and v0.3+).

For each sample where both versions exist, extract:
- profile type (after schema-normalizing)
- extrude extent_type, direction, distance
- key dimension(s) (radius/outer_radius+inner_radius/length_u+width_v/straight_length+radius)
- part_category

Classify each numeric field as:
- MATCH (within 1% relative tolerance)
- DIFF (numeric values differ)
- PARTIAL (hand has it, comp doesn't, or vice versa) — due to schema diff
- NA (neither has the field meaningfully)
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
    if not d.exists():
        continue
    # hand-written files have suffix .design_plan (no .json); glob both
    for p in list(d.glob("*.design_plan.json")) + list(d.glob("*.design_plan")):
        if p.is_file():
            sid = p.stem.replace(".design_plan", "")
            if sid not in HAND_WRITTEN:
                HAND_WRITTEN[sid] = (p, ver)


def extract_hand_profile_type(hand, ver):
    """Schema-normalized: v0.2 uses 'profile.type', v0.3+ uses 'profiles[0].type'."""
    if ver in ("v0.2", "design_plan_v0.2"):
        sb = hand.get("solid_bodies", [{}])[0]
        return sb.get("profile", {}).get("type")
    sb = hand.get("solid_bodies", [{}])[0]
    profiles = sb.get("profiles") or [{}]
    return profiles[0].get("type") if profiles else None


def extract_hand_radius(hand, ver):
    """v0.2 uses profile.parameters.side_u/side_v/radius. v0.3+ uses dimensions.profiles[]."""
    sb = hand.get("solid_bodies", [{}])[0]
    if ver in ("v0.2", "design_plan_v0.2"):
        params = sb.get("profile", {}).get("parameters", {})
        # v0.2 dimensions: rect uses side_u/side_v; circle/annulus use radius
        if "radius" in params:
            return params["radius"].get("value")
        return None
    dims = sb.get("dimensions", {})
    pd = dims.get("profiles", [{}])[0] if dims.get("profiles") else {}
    return pd.get("radius", {}).get("value") if isinstance(pd, dict) else None


def extract_hand_rect_dims(hand, ver):
    sb = hand.get("solid_bodies", [{}])[0]
    if ver in ("v0.2", "design_plan_v0.2"):
        params = sb.get("profile", {}).get("parameters", {})
        lu = params.get("side_u", {}).get("value")
        wv = params.get("side_v", {}).get("value")
        return (lu, wv)
    dims = sb.get("dimensions", {})
    pd = dims.get("profiles", [{}])[0] if dims.get("profiles") else {}
    return (pd.get("length_u", {}).get("value"), pd.get("width_v", {}).get("value"))


def extract_hand_annulus_radii(hand, ver):
    sb = hand.get("solid_bodies", [{}])[0]
    if ver in ("v0.2", "design_plan_v0.2"):
        params = sb.get("profile", {}).get("parameters", {})
        # v0.2 doesn't distinguish outer/inner for annulus directly; just has radii
        ro = params.get("outer_radius", {}).get("value")
        ri = params.get("inner_radius", {}).get("value")
        return (ro, ri)
    dims = sb.get("dimensions", {})
    pd = dims.get("profiles", [{}])[0] if dims.get("profiles") else {}
    return (pd.get("outer_radius", {}).get("value"), pd.get("inner_radius", {}).get("value"))


def extract_hand_stadium(hand, ver):
    sb = hand.get("solid_bodies", [{}])[0]
    if ver in ("v0.2", "design_plan_v0.2"):
        params = sb.get("profile", {}).get("parameters", {})
        return (params.get("straight_length", {}).get("value"),
                params.get("radius", {}).get("value"))
    dims = sb.get("dimensions", {})
    pd = dims.get("profiles", [{}])[0] if dims.get("profiles") else {}
    return (pd.get("straight_length", {}).get("value"),
            pd.get("radius", {}).get("value"))


def extract_hand_extrude(hand, ver):
    sb = hand.get("solid_bodies", [{}])[0]
    ex = sb.get("extrude", {}) or sb.get("extrude_block", {})  # both spellings seen
    return ex


def classify(hv, cv, tol_pct=0.01, unit_factor=1.0):
    """Classify a value comparison. unit_factor scales hv (e.g. 10 for cm->mm)."""
    if hv is None and cv is None:
        return "NA"
    if hv is None or cv is None:
        return "PARTIAL"
    if isinstance(hv, str) or isinstance(cv, str):
        return "MATCH" if str(hv) == str(cv) else "DIFF"
    try:
        hv_f = float(hv) * unit_factor
        cv_f = float(cv)
    except (ValueError, TypeError):
        return "MATCH" if hv == cv else "DIFF"
    base = max(abs(hv_f), abs(cv_f), 1.0)
    if abs(hv_f - cv_f) / base < tol_pct:
        return "MATCH"
    return "DIFF"


# Run comparison
m = json.load(open(ROOT / "data/sanity_set_50/manifest.json", encoding="utf-8"))
IDS = [e["id"] for e in m["entries"]]

print("=" * 80)
print("FREEZE ASSESSMENT: hand-written (any version) vs compiler_v6 output")
print("=" * 80)
print(f"{len(HAND_WRITTEN)} samples have hand-written plans, 5 (samples 6-10) do not")
print()

results = []
for sid in IDS:
    if sid not in HAND_WRITTEN:
        continue
    hp, hver = HAND_WRITTEN[sid]
    cp = COMPILER_OUT / f"{sid}.design_plan.json"
    if not cp.exists():
        continue
    hand = json.loads(hp.read_text(encoding="utf-8"))
    comp = json.loads(cp.read_text(encoding="utf-8"))
    cver = comp.get("schema_version", "?")

    h_ptype = extract_hand_profile_type(hand, hver.replace("design_plan_", ""))
    c_ptype = (comp.get("solid_bodies", [{}])[0].get("profiles") or [{}])[0].get("type")
    ptype_class = classify(h_ptype, c_ptype)

    # Extrude
    hex = extract_hand_extrude(hand, hver.replace("design_plan_", ""))
    cex = comp.get("solid_bodies", [{}])[0].get("extrude", {})
    etype_class = classify((hex or {}).get("extent_type"), cex.get("extent_type"))
    edir_class = classify((hex or {}).get("direction"), cex.get("direction"))

    # Key dimensions by profile type (apply unit conversion: v0.2/v0.3 hand dims are in cm)
    h_unit_factor = 10.0 if hver.replace("design_plan_", "") in ("v0.2", "v0.3") else 1.0
    if ptype_class == "MATCH":
        if h_ptype == "circle" or c_ptype == "circle":
            hr = extract_hand_radius(hand, hver.replace("design_plan_", ""))
            cr = (comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("radius", {}).get("value"))
            r_class = classify(hr, cr, unit_factor=h_unit_factor)
        elif h_ptype in ("annulus",) or c_ptype in ("annulus",):
            ho, hi = extract_hand_annulus_radii(hand, hver.replace("design_plan_", ""))
            co, ci = (comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("outer_radius", {}).get("value"),
                     comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("inner_radius", {}).get("value"))
            o_class = classify(ho, co, unit_factor=h_unit_factor)
            i_class = classify(hi, ci, unit_factor=h_unit_factor)
            r_class = f"outer:{o_class}/inner:{i_class}"
        elif h_ptype == "stadium" or c_ptype == "stadium":
            hs, hr = extract_hand_stadium(hand, hver.replace("design_plan_", ""))
            cs = comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("straight_length", {}).get("value")
            cr = comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("radius", {}).get("value")
            sl_class = classify(hs, cs, unit_factor=h_unit_factor)
            r_class = f"straight:{sl_class}/r:{classify(hr, cr, unit_factor=h_unit_factor)}"
        elif h_ptype == "rectangle" or c_ptype == "rectangle":
            hlu, hwv = extract_hand_rect_dims(hand, hver.replace("design_plan_", ""))
            clu = comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("length_u", {}).get("value")
            cwv = comp.get("solid_bodies", [{}])[0].get("dimensions", {}).get("profiles", [{}])[0].get("width_v", {}).get("value")
            lu_class = classify(hlu, clu, unit_factor=h_unit_factor)
            wv_class = classify(hwv, cwv, unit_factor=h_unit_factor)
            r_class = f"lu:{lu_class}/wv:{wv_class}"
        else:
            r_class = "N/A"
    else:
        r_class = "SKIP(ptype diff)"

    # Apply unit conversion to extrude distance
    edist_re = classify(
        (hex or {}).get("distance_total") if (hex or {}).get("distance_total") else
        (((hex or {}).get("distance") or {}).get("value") if isinstance((hex or {}).get("distance"), dict) else (hex or {}).get("distance")),
        cex.get("distance_total", {}).get("value"),
        unit_factor=h_unit_factor,
    )
    edist_class = edist_re

    # part_category (non-verifiable, just informational)
    h_pc = hand.get("target", {}).get("part_category")
    c_pc = comp.get("target", {}).get("part_category")
    pc_class = classify(h_pc, c_pc)

    results.append({
        "sid": sid, "hver": hver, "cver": cver,
        "ptype": ptype_class,
        "etype": etype_class,
        "edir": edir_class,
        "edist": edist_class,
        "dims": r_class,
        "part_cat": pc_class,
    })

# Aggregate
counts = Counter()
for r in results:
    for k in ("ptype", "etype", "edir", "edist", "dims", "part_cat"):
        v = r[k]
        # parse multi-value fields
        for sub in v.split("/") if "/" in v else [v]:
            sub = sub.strip()
            counts[(k, sub)] += 1

print("=" * 80)
print("AGGREGATE FIELD-LEVEL CLASSIFICATION (across 45 samples)")
print("=" * 80)
print(f"{'field':<10} {'class':<10} {'count'}")
print("-" * 30)
for (field, cls), cnt in sorted(counts.items()):
    print(f"{field:<10} {cls:<10} {cnt}")
print()

# Per-sample summary table
print("=" * 80)
print("PER-SAMPLE SUMMARY (only those with DIFF/PARTIAL/NA — non-MATCH)")
print("=" * 80)
for r in results:
    bad = [k for k in ("ptype", "etype", "edir", "edist") if r[k] not in ("MATCH", "NA")]
    bad_dims = r["dims"] if any(c not in ("MATCH", "NA", "N/A", "SKIP(ptype diff)") for c in r["dims"].split("/") if c.strip()) else "MATCH"
    if bad or "DIFF" in r["dims"] or "PARTIAL" in r["dims"]:
        print(f"\n  {r['sid']} ({r['hver']}->{r['cver']})")
        print(f"    ptype: {r['ptype']}  etype: {r['etype']}  edir: {r['edir']}  edist: {r['edist']}")
        print(f"    dims:  {r['dims']}")
        print(f"    part_cat: {r['part_cat']}")
    elif r["ptype"] == "DIFF":
        print(f"\n  {r['sid']} ({r['hver']}->{r['cver']}): profile.type mismatch: hand={r['ptype']} comp={r['ptype']}")
