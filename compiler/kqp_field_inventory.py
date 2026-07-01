"""Enumerate all KQP-queryable fields across the 50 v6 design plan instances.

For each sample, walk the design plan and emit a list of (field_path, field_value,
field_category) tuples where field_category ∈:
  - 'topology' (→ A: body_count, face_count, etc.)
  - 'geometry_dim' (→ B: bbox_x, radius, etc.)
  - 'feature' (→ C: through_void_count, hole_radius, etc.)
  - 'health' (→ D: occt_valid, is_solid)
  - 'metadata' (not directly queryable, but informative)

Output: aggregate_field_inventory.json with per-sample facts and global stats.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "compiler" / "instances_v6"

# Map design_plan_v0.6 fields → KQP query category
# (Verification gate: KQP asks the OCCT kernel; field must be observably queryable)
FIELD_MAP = {
    # === A. TOPOLOGY ===
    "target.body_count": ("topology", "body_count"),
    "solid_bodies.0.id": ("metadata", None),
    # === B. GEOMETRY / DIMENSIONS ===
    "solid_bodies.0.frame.u_dir": ("metadata", None),
    "solid_bodies.0.frame.v_dir": ("metadata", None),
    "solid_bodies.0.frame.w_dir": ("metadata", None),
    "solid_bodies.0.extrude.extent_type": ("metadata", None),
    "solid_bodies.0.extrude.direction": ("metadata", None),
    "solid_bodies.0.extrude.distance_total.value": ("geometry_dim", "extrude_distance"),
    "solid_bodies.0.dimensions.extrude_distance.value": ("geometry_dim", "extrude_distance"),
    # profile-specific dims
    "solid_bodies.0.dimensions.profiles.0.length_u.value": ("geometry_dim", "bbox_size"),
    "solid_bodies.0.dimensions.profiles.0.width_v.value": ("geometry_dim", "bbox_size"),
    "solid_bodies.0.dimensions.profiles.0.radius.value": ("geometry_dim", "cylinder_radius"),
    "solid_bodies.0.dimensions.profiles.0.outer_radius.value": ("geometry_dim", "cylinder_radius"),
    "solid_bodies.0.dimensions.profiles.0.inner_radius.value": ("geometry_dim", "cylinder_radius"),
    "solid_bodies.0.dimensions.profiles.0.straight_length.value": ("geometry_dim", "bbox_size"),
    "solid_bodies.0.dimensions.profiles.0.center_uv": ("metadata", None),
    # arbitrary_closed generic dims (v0.5+)
    "solid_bodies.0.dimensions.profiles.0.arc_radii": ("geometry_dim", "curve_radius_list"),
    "solid_bodies.0.dimensions.profiles.0.line_lengths": ("geometry_dim", "edge_length_list"),
    "solid_bodies.0.dimensions.profiles.0.circle_radii": ("geometry_dim", "curve_radius_list"),
    # === C. FEATURE (voids/holes) ===
    "solid_bodies.0.profiles.0.rings": ("feature", "rings"),  # count inner rings → through_void_count
    # === D. HEALTH ===
    # (compiler doesn't yet emit health-related fields directly; derived from topology)
    # === TARGET / METADATA ===
    "target.object_type": ("metadata", None),
    "target.part_category": ("metadata", None),
    "target.engineering_description": ("metadata", None),
}


def get_field(data, path):
    """Walk a dotted path like 'solid_bodies.0.profiles.0.rings' returning the value or None."""
    cur = data
    for k in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(k)
        elif isinstance(cur, list):
            try:
                k = int(k)
            except (ValueError, TypeError):
                return None
            if 0 <= k < len(cur):
                cur = cur[k]
            else:
                return None
        else:
            return None
        if cur is None:
            return None
    return cur


def has_inner_ring(profile):
    """True if profile has at least one ring with role='inner'."""
    rings = profile.get("rings", []) or []
    return any(r.get("role") == "inner" for r in rings)


def count_inner_rings(profile):
    return sum(1 for r in profile.get("rings", []) or [] if r.get("role") == "inner")


def classify_ptype_kqps(ptype, has_inner):
    """Given profile.type and presence of inner rings, list KQP queries applicable."""
    queries = []
    if ptype in ("rectangle", "circle", "annulus", "stadium", "polygon_with_fillets", "rectangular_frame", "arbitrary_closed"):
        queries.append({"intent": "body_count", "expected_source": "$.target.body_count"})
        queries.append({"intent": "face_count", "expected_source": "(derived from topology)"})
        queries.append({"intent": "is_solid", "expected": True})
        queries.append({"intent": "occt_valid", "expected": True})
    return queries


per_sample_facts = []
global_field_coverage = Counter()
global_kqp_query_intents = Counter()

IDS = sorted(p.stem.replace(".design_plan", "")
              for p in INSTANCES.glob("*.design_plan.json"))
print(f"Total instances: {len(IDS)}")

for sid in IDS:
    p = INSTANCES / f"{sid}.design_plan.json"
    data = json.loads(p.read_text(encoding="utf-8"))

    facts = []
    # 1) target.body_count
    bc = data.get("target", {}).get("body_count")
    if bc is not None:
        facts.append({"field_path": "target.body_count", "value": bc,
                      "category": "topology",
                      "query_intent": "body_count",
                      "source_field": "$.target.body_count",
                      "feedback_enabled": True})
        global_field_coverage["target.body_count"] += 1
        global_kqp_query_intents["body_count"] += 1

    # 2) extrude_distance / bbox dims
    sb = data.get("solid_bodies", [{}])[0]
    dims = sb.get("dimensions", {})
    extrude_mm = dims.get("extrude_distance", {}).get("value")
    if extrude_mm is not None:
        facts.append({"field_path": "solid_bodies.0.dimensions.extrude_distance.value",
                      "value": extrude_mm, "category": "geometry_dim",
                      "query_intent": "bbox_size_axis_w (extrude axis)",
                      "source_field": "$.solid_bodies[0].dimensions.extrude_distance.value",
                      "feedback_enabled": True})
        global_field_coverage["extrude_distance"] += 1
        global_kqp_query_intents["bbox_size"] += 1

    profiles = sb.get("profiles", [{}])
    if profiles:
        p0 = profiles[0]
        ptype = p0.get("type")
        pdims = dims.get("profiles", [{}])[0]

        # span fields → bbox_size
        if ptype == "rectangle":
            lu = pdims.get("length_u", {}).get("value")
            wv = pdims.get("width_v", {}).get("value")
            if lu is not None:
                facts.append({"field_path": "length_u", "value": lu, "category": "geometry_dim",
                              "query_intent": "bbox_size_axis_u",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].length_u.value",
                              "feedback_enabled": True})
                global_field_coverage["length_u"] += 1
                global_kqp_query_intents["bbox_size"] += 1
            if wv is not None:
                facts.append({"field_path": "width_v", "value": wv, "category": "geometry_dim",
                              "query_intent": "bbox_size_axis_v",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].width_v.value",
                              "feedback_enabled": True})
                global_field_coverage["width_v"] += 1
                global_kqp_query_intents["bbox_size"] += 1
        elif ptype == "stadium":
            sl = pdims.get("straight_length", {}).get("value")
            rd = pdims.get("radius", {}).get("value")
            if sl is not None:
                facts.append({"field_path": "straight_length", "value": sl,
                              "category": "geometry_dim",
                              "query_intent": "stadium_length_via_u (union span)",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].straight_length.value",
                              "feedback_enabled": True})
                global_field_coverage["straight_length"] += 1
            if rd is not None:
                facts.append({"field_path": "stadium_radius", "value": rd,
                              "category": "geometry_dim",
                              "query_intent": "bbox_size_axis_v (2*radius)",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].radius.value",
                              "feedback_enabled": True})
                global_field_coverage["stadium_radius"] += 1
            global_kqp_query_intents["bbox_size"] += 1
        elif ptype == "circle":
            r = pdims.get("radius", {}).get("value")
            if r is not None:
                facts.append({"field_path": "circle_radius", "value": r,
                              "category": "geometry_dim",
                              "query_intent": "cylinder_radius (bbox u/v = 2r)",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].radius.value",
                              "feedback_enabled": True})
                global_field_coverage["circle_radius"] += 1
                global_kqp_query_intents["cylinder_radius"] += 1
                global_kqp_query_intents["bbox_size"] += 1
        elif ptype == "annulus":
            ro = pdims.get("outer_radius", {}).get("value")
            ri = pdims.get("inner_radius", {}).get("value")
            if ro is not None:
                facts.append({"field_path": "outer_radius", "value": ro,
                              "category": "geometry_dim",
                              "query_intent": "annulus_outer (bbox u/v = 2*ro)",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value",
                              "feedback_enabled": True})
                global_field_coverage["outer_radius"] += 1
                global_kqp_query_intents["cylinder_radius"] += 1
            if ri is not None:
                facts.append({"field_path": "inner_radius", "value": ri,
                              "category": "geometry_dim",
                              "query_intent": "annulus_inner (hole_radius)",
                              "source_field": "$.solid_bodies[0].dimensions.profiles[0].inner_radius.value",
                              "feedback_enabled": True})
                global_field_coverage["inner_radius"] += 1
            global_kqp_query_intents["bbox_size"] += 1
        elif ptype == "rectangular_frame":
            olu = pdims.get("outer_length_u", {}).get("value")
            owv = pdims.get("outer_width_v", {}).get("value")
            ilu = pdims.get("inner_length_u", {}).get("value")
            iwv = pdims.get("inner_width_v", {}).get("value")
            for nm, v in (("outer_length_u", olu), ("outer_width_v", owv),
                           ("inner_length_u", ilu), ("inner_width_v", iwv)):
                if v is not None:
                    facts.append({"field_path": nm, "value": v, "category": "geometry_dim",
                                  "query_intent": f"rect_frame_{nm}",
                                  "source_field": f"$.solid_bodies[0].dimensions.profiles[0].{nm}.value",
                                  "feedback_enabled": True})
                    global_field_coverage[nm] += 1
            global_kqp_query_intents["bbox_size"] += 1
        elif ptype == "arbitrary_closed":
            arcs = pdims.get("arc_radii", [])
            lines = pdims.get("line_lengths", [])
            circles = pdims.get("circle_radii", [])
            for i, item in enumerate(arcs):
                facts.append({"field_path": f"arc_radii[{i}]", "value": item.get("value"),
                              "category": "geometry_dim",
                              "query_intent": f"arbitrary_arc_{i}_radius",
                              "source_field": f"$.solid_bodies[0].dimensions.profiles[0].arc_radii[{i}].value",
                              "feedback_enabled": True})
                global_field_coverage["arc_radii"] += 1
            for i, item in enumerate(lines):
                facts.append({"field_path": f"line_lengths[{i}]", "value": item.get("value"),
                              "category": "geometry_dim",
                              "query_intent": f"arbitrary_line_{i}_length",
                              "source_field": f"$.solid_bodies[0].dimensions.profiles[0].line_lengths[{i}].value",
                              "feedback_enabled": True})
                global_field_coverage["line_lengths"] += 1

        # rings → through_void_count (feature query C)
        n_inner = count_inner_rings(p0)
        if n_inner > 0:
            facts.append({"field_path": "inner_rings_count", "value": n_inner,
                          "category": "feature",
                          "query_intent": "through_void_count",
                          "expected": n_inner,
                          "source_field": "$.solid_bodies[0].profiles[0].rings[*].role=='inner' count",
                          "feedback_enabled": True})
            global_field_coverage["inner_rings_count"] += 1
            global_kqp_query_intents["through_void_count"] += 1

        # ALWAYS-emitted health queries (D)
        facts.append({"field_path": "is_solid_inferred", "value": True, "category": "health",
                      "query_intent": "is_solid", "expected": True,
                      "source_field": "$.target.body_count == 1",
                      "feedback_enabled": True})
        facts.append({"field_path": "occt_valid_inferred", "value": True, "category": "health",
                      "query_intent": "occt_valid", "expected": True,
                      "source_field": "(implied by valid SKETCH + EXTRUDE)",
                      "feedback_enabled": True})
        global_kqp_query_intents["is_solid"] += 1
        global_kqp_query_intents["occt_valid"] += 1

    per_sample_facts.append({
        "sid": sid,
        "profile_type": ptype if profiles else None,
        "facts": facts,
    })

# Output
out_dir = ROOT / "compiler" / "kqp_field_inventory"
out_dir.mkdir(exist_ok=True)
out_dir.joinpath("per_sample_facts.json").write_text(
    json.dumps(per_sample_facts, indent=2, ensure_ascii=False), encoding="utf-8")
out_dir.joinpath("aggregate.json").write_text(json.dumps({
    "samples": len(per_sample_facts),
    "field_coverage": dict(global_field_coverage),
    "kqp_query_intents": dict(global_kqp_query_intents),
}, indent=2), encoding="utf-8")

print("=" * 70)
print("FIELD ENUMERATION ACROSS 50 v6 INSTANCES")
print("=" * 70)
print(f"Total instances analyzed: {len(per_sample_facts)}")
print()
print("Per-field coverage (out of 50):")
for f, c in global_field_coverage.most_common():
    print(f"  {f:<25}: {c:3d}/50  ({c/50*100:.0f}%)")
print()
print("KQP query intents triggered:")
for q, c in global_kqp_query_intents.most_common():
    print(f"  {q:<25}: {c} occurrences")
print()
print(f"Per-sample fact dumps → {out_dir}/per_sample_facts.json")
print(f"Aggregate summary       → {out_dir}/aggregate.json")
