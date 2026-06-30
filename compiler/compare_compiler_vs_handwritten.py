"""Compare compiler_v6 output vs hand-written Design Plans for the 45 samples
where both exist. Identify:
  - schema-level differences (structural fields present/absent)
  - semantic differences (profile.type, key dimensions, direction, etc.)

Reports:
  - per-sample key field table
  - aggregate counts of each type of divergence
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "DesignPlan" / "samples"
COMPILER_OUT = ROOT / "compiler" / "instances_v6"

# find all hand-written plans with their schema version
HAND_WRITTEN = {}  # sid -> (path, schema_version)
for ver, subdir in [("v0.2", "v2"), ("v0.3", "v3"), ("v0.4", "v4"),
                     ("v0.5", "v5"), ("v0.6", "v6")]:
    d = SAMPLES / subdir
    if not d.exists():
        continue
    for p in d.glob("*.design_plan.json"):
        sid = p.stem.replace(".design_plan", "")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sv = data.get("schema_version", "")
            HAND_WRITTEN[sid] = (p, sv)
        except Exception:
            pass


def dim_val(d, *path, default=None):
    cur = d
    for k in path:
        if isinstance(cur, dict) and isinstance(k, str):
            cur = cur.get(k)
        elif isinstance(cur, list) and isinstance(k, int):
            cur = cur[k] if 0 <= k < len(cur) else None
        else:
            return default
        if cur is None:
            return default
    return cur.get("value") if isinstance(cur, dict) and "value" in cur else cur


def get_handwritten(sid):
    if sid not in HAND_WRITTEN:
        return None
    return json.loads(HAND_WRITTEN[sid][0].read_text(encoding="utf-8"))


def get_compiler(sid):
    p = COMPILER_OUT / f"{sid}.design_plan.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# Key fields to compare
FIELDS = [
    ("profile.type", lambda d: dim_val(d, "solid_bodies", 0, "profiles", 0, "type")),
    ("extrude.extent_type", lambda d: dim_val(d, "solid_bodies", 0, "extrude", "extent_type")),
    ("extrude.direction", lambda d: dim_val(d, "solid_bodies", 0, "extrude", "direction")),
    ("extrude_distance", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "extrude_distance")),
    ("radius", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")),
    ("outer_radius", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_radius")),
    ("inner_radius", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "inner_radius")),
    ("length_u", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "length_u")),
    ("width_v", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "width_v")),
    ("straight_length", lambda d: dim_val(d, "solid_bodies", 0, "dimensions", "profiles", 0, "straight_length")),
    ("part_category", lambda d: dim_val(d, "target", "part_category")),
]

# Aggregate stats
DIVERGENCE_TYPES = Counter()
PER_SAMPLE = {}

m = json.load(open(ROOT / "data/sanity_set_50/manifest.json", encoding="utf-8"))
IDS = [e["id"] for e in m["entries"]]

for sid in IDS:
    hand = get_handwritten(sid)
    comp = get_compiler(sid)
    if hand is None or comp is None:
        continue
    h_schema = hand.get("schema_version", "?")
    c_schema = comp.get("schema_version", "?")

    diffs = []
    for fname, extractor in FIELDS:
        hv = extractor(hand)
        cv = extractor(comp)
        if hv is None and cv is None:
            continue
        if isinstance(hv, float) and isinstance(cv, float):
            if abs(hv - cv) < 0.01 * max(abs(hv), abs(cv), 1.0):
                continue
        if hv == cv:
            continue
        # Schema-level diffs (structural fields missing in one)
        if fname == "profile.type":
            DIVERGENCE_TYPES["profile.type mismatch"] += 1
        elif fname in ("radius", "outer_radius", "inner_radius", "length_u", "width_v", "straight_length", "extrude_distance"):
            if hv is None or cv is None:
                DIVERGENCE_TYPES[f"{fname} missing (one side)"] += 1
            else:
                DIVERGENCE_TYPES[f"{fname} value mismatch"] += 1
        elif fname == "part_category":
            DIVERGENCE_TYPES["part_category differs (non-verifiable)"] += 1
        else:
            DIVERGENCE_TYPES[f"{fname} differs"] += 1
        diffs.append((fname, hv, cv))

    PER_SAMPLE[sid] = {
        "hand_schema": h_schema,
        "comp_schema": c_schema,
        "diffs": diffs,
        "diff_count": len(diffs),
    }

# Print summary
print("=" * 80)
print("Schema / semantic comparison: hand-written vs compiler_v6 output")
print("=" * 80)
print(f"Compared samples: {len(PER_SAMPLE)} (out of 50, missing 6-10 + no hand-written)")
print()
print("Aggregate divergence counts:")
for k, v in DIVERGENCE_TYPES.most_common():
    print(f"  {k}: {v}")
print()

# Per-sample breakdown
print("=" * 80)
print("Per-sample diff details (only samples with diffs)")
print("=" * 80)
any_diff = False
for sid, info in sorted(PER_SAMPLE.items(), key=lambda x: x[1]["diff_count"], reverse=True):
    if info["diff_count"] > 0:
        any_diff = True
        print(f"\n[{sid}]  hand={info['hand_schema']}, comp={info['comp_schema']}, diffs={info['diff_count']}")
        for fname, hv, cv in info["diffs"]:
            print(f"  {fname}: hand={hv!r}  comp={cv!r}")
if not any_diff:
    print("(none — compiler output exactly matches hand-written)")

# Categorize: minor (acceptable) vs fundamental
print()
print("=" * 80)
print("FREEZE ASSESSMENT")
print("=" * 80)
n_samples = len(PER_SAMPLE)
n_exact = sum(1 for s in PER_SAMPLE.values() if s["diff_count"] == 0)
n_with_diffs = n_samples - n_exact
print(f"Exact match: {n_exact}/{n_samples}")
print(f"With diffs: {n_with_diffs}/{n_samples}")

# detailed categorization
print("\nSchema-level diffs (presence/absence of fields, not values):")
schema_diff = 0
value_diff = 0
for sid, info in PER_SAMPLE.items():
    for fname, hv, cv in info["diffs"]:
        if hv is None or cv is None:
            schema_diff += 1
        else:
            value_diff += 1
print(f"  Schema-level (one side missing): {schema_diff}")
print(f"  Value-level (both have values, differ): {value_diff}")
