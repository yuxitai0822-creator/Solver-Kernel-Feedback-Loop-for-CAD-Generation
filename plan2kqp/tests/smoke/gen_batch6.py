"""Generate batch 6 (samples 41-50) KQP instances to v0.2 directory."""
import json
from pathlib import Path
ROOT = Path(r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
KQP_DIR = ROOT / 'KQP' / 'samples' / 'v0.2'
KQP_DIR.mkdir(exist_ok=True)
SAMPLES = [
    # annulus
    ('107668_cf76b132_0001', 'annulus', {'ro': 132.5, 'ri': 75.0, 'dist': 100.0, 'dir': '+w', 'voids': 1}),
    # rectangle 0-dimension (sample 42) — uses point_span inference
    ('108244_329b1876_0000', 'rectangle_0d', {'lu': 1219.2, 'wv': 2590.8, 'dist': 44.45, 'dir': '+w'}),
    # rectangle (sample 43 large panel)
    ('108412_8de2f9c3_0000', 'rectangle', {'lu': 2438.4, 'wv': 1219.2, 'dist': 12.7, 'dir': '+w'}),
    # rectangles (samples 44, 45, 46, 47, 48, 49) — standard
    ('108850_0dcd5ef1_0002', 'rectangle', {'lu': 171.45, 'wv': 38.1, 'dist': 6.35, 'dir': '+w'}),
    ('108850_0dcd5ef1_0004', 'rectangle', {'lu': 171.45, 'wv': 110.998, 'dist': 6.35, 'dir': '+w'}),
    ('108851_4d515b10_0005', 'rectangle', {'lu': 307.848, 'wv': 19.05, 'dist': 12.7, 'dir': '+w'}),
    ('108851_4d515b10_0006', 'rectangle', {'lu': 95.25, 'wv': 19.05, 'dist': 12.7, 'dir': '+w'}),
    ('108851_4d515b10_0007', 'rectangle', {'lu': 279.4, 'wv': 50.8, 'dist': 19.05, 'dir': '+w'}),
    ('108851_4d515b10_0009', 'rectangle', {'lu': 209.55, 'wv': 57.912, 'dist': 19.05, 'dir': '+w'}),
    # circle (sample 50 — long pin with FLIPPED frame)
    ('108852_fed54702_0004', 'circle', {'radius': 3.96875, 'dist': 139.7, 'dir': '+w'}),
]


def add_bbox(queries, axis, val, src, extra=""):
    if not val:
        return
    queries.append({
        "id": f"q_bbox_{axis}", "category": "B_geometry_dim", "intent": "bbox_size",
        "axis": axis, "expected": val,
        "tolerance": max(0.05, val * 1e-4),
        "source_field": src, "feedback_enabled": True,
        "feedback_template": f"Expected bbox {axis}-size {val}mm{extra}, got {{actual}}mm."
    })


for sid, ptype, p in SAMPLES:
    queries = [{
        "id": "q_body_count", "category": "A_topology", "intent": "body_count",
        "expected": 1, "source_field": "$.target.body_count",
        "feedback_enabled": True,
        "feedback_template": "Expected body_count=1, got {actual}."
    }]

    if ptype in ("rectangle", "rectangle_0d"):
        # In v0.2, rectangle_0d (no explicit dims) uses inference_mode=all
        # and source_field annotates this.
        sf_u = "$.solid_bodies[0].dimensions.profiles[0].length_u.value"
        sf_v = "$.solid_bodies[0].dimensions.profiles[0].width_v.value"
        # Source suffix to flag inference mode
        if ptype == "rectangle_0d":
            sf_u += " (inferred_from_point_span)"
            sf_v += " (inferred_from_point_span)"
        add_bbox(queries, "u", p["lu"], sf_u)
        add_bbox(queries, "v", p["wv"], sf_v)
    elif ptype == "circle":
        r = p["radius"]
        add_bbox(queries, "u", 2 * r,
                 "$.solid_bodies[0].dimensions.profiles[0].radius.value (computed: 2*r)")
        add_bbox(queries, "v", 2 * r,
                 "$.solid_bodies[0].dimensions.profiles[0].radius.value (computed: 2*r)")
        queries.append({
            "id": "q_radius", "category": "B_geometry_dim", "intent": "cylinder_radius",
            "expected": r, "tolerance": 0.01,
            "source_field": "$.solid_bodies[0].dimensions.profiles[0].radius.value",
            "feedback_enabled": True,
            "feedback_template": f"Expected cylinder radius {r}mm, got {{actual}}mm."
        })
    elif ptype == "annulus":
        ro, ri = p["ro"], p["ri"]
        for sel, val, src in [
            ("outer", ro, "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value"),
            ("inner", ri, "$.solid_bodies[0].dimensions.profiles[0].inner_radius.value"),
        ]:
            queries.append({
                "id": f"q_{sel}_radius", "category": "B_geometry_dim", "intent": "cylinder_radius",
                "params": {"selector": sel}, "expected": val, "tolerance": 0.01,
                "source_field": src, "feedback_enabled": True,
                "feedback_template": f"Expected {sel} cylinder radius {val}mm, got {{actual}}mm."
            })
        add_bbox(queries, "u", 2 * ro,
                 "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value (computed: 2*r)")
        add_bbox(queries, "v", 2 * ro,
                 "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value (computed: 2*r)")

    voids = p.get("voids", 0)
    if voids:
        queries.append({
            "id": "q_void_count", "category": "C_feature", "intent": "through_void_count",
            "expected": voids, "tolerance": 0,
            "source_field": "$.solid_bodies[0].profiles[0].rings[*].role=='inner' count",
            "feedback_enabled": True, "feedback_template": f"Expected {voids} through-void(s), got {{actual}}."
        })

    dist = p.get("dist", 0)
    add_bbox(queries, "w", dist, "$.solid_bodies[0].dimensions.extrude_distance.value")

    queries.append({
        "id": "q_is_solid", "category": "D_health", "intent": "is_solid",
        "expected": True, "source_field": "(implicit: valid extrude implies solid)",
        "feedback_enabled": True, "feedback_template": "Body is not a closed solid. got {actual}."
    })
    queries.append({
        "id": "q_occt_valid", "category": "D_health", "intent": "occt_valid",
        "expected": True, "source_field": "(implicit)",
        "feedback_enabled": True, "feedback_template": "OCCT validation failed. got {actual}."
    })

    instance = {
        "schema_version": "kqp_instance_v0.2",
        "instance_id": f"kqp_{sid}",
        "design_plan_id": sid,
        "step_file": f"data/sanity_set_50/{sid}.step",
        "queries": queries
    }
    out = KQP_DIR / f"{sid}.kqp_instance.json"
    out.write_text(json.dumps(instance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote v0.2: {sid} ({ptype}, {len(queries)} queries)")
