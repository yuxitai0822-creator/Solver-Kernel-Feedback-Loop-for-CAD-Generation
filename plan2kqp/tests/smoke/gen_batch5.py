"""Generate batch 5 (samples 31-40) KQP instances to v0.2 directory."""
import json
from pathlib import Path
ROOT = Path(r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
KQP_DIR = ROOT / 'KQP' / 'samples' / 'v0.2'
KQP_DIR.mkdir(exist_ok=True)
SAMPLES = [
    ('105278_909f3813_0000', 'rectangle', {'lu': 12.0, 'wv': 60.0, 'dist': 40.0, 'dir': '+w'}),
    ('106323_77f22d29_0004', 'annulus', {'ro': 17.5, 'ri': 12.5, 'dist': 10.0, 'dir': 'both_symmetric', 'extent': 'symmetric', 'voids': 1}),
    ('106817_bb28b7aa_0002', 'circle', {'radius': 4.87045, 'dist': 6.8707, 'dir': '+w'}),
    ('106817_bb28b7aa_0003', 'circle', {'radius': 4.7117, 'dist': 12.192, 'dir': '+w'}),
    ('106817_bb28b7aa_0004', 'annulus', {'ro': 5.5372, 'ri': 1.9812, 'dist': 1.3208, 'dir': '+w', 'voids': 1}),
    ('107055_0500fdd1_0027', 'annulus', {'ro': 3.49, 'ri': 2.0, 'dist': 0.36, 'dir': '-w', 'voids': 1}),
    ('107075_beb19139_0000', 'arbitrary_closed', {'dist': 25.4, 'dir': '+w'}),
    ('107466_72cd4ce9_0002', 'stadium', {'sl': 80.0, 'r': 10.0, 'dist': 10.0, 'dir': '+w', 'extent': 'degenerate_two_side', 'voids': 2}),
    ('107467_a8afc51d_0000', 'circle', {'radius': 3.0, 'dist': 14.0, 'dir': '+w'}),
    ('107467_a8afc51d_0002', 'circle', {'radius': 3.0, 'dist': 25.0, 'dir': '+w'}),
]


def add_bbox(queries, axis, val, src, extra=""):
    if not val:
        return
    queries.append({
        "id": f"q_bbox_{axis}", "category": "B_geometry_dim", "intent": "bbox_size",
        "axis": axis, "expected": val,
        "tolerance": max(0.01, val * 1e-4),
        "source_field": src, "feedback_enabled": True,
        "feedback_template": f"Expected bbox {axis}-size {val}mm{extra}, got {{actual}}mm."
    })


def add_health(queries, dir_sign, extent, dist):
    direction_note = " (negative extrude)" if dir_sign == "-w" else ""
    extra_note = ""
    if extent == "symmetric":
        extra_note = " (symmetric extrude, body straddles plane)"
    elif extent == "degenerate_two_side":
        extra_note = " (degenerate two_side, extent_two=0)"
    queries.append({
        "id": "q_bbox_w", "category": "B_geometry_dim", "intent": "bbox_size",
        "axis": "w", "expected": dist,
        "tolerance": max(0.01, dist * 1e-4),
        "source_field": "$.solid_bodies[0].dimensions.extrude_distance.value",
        "feedback_enabled": True,
        "feedback_template": f"Expected bbox w-size {dist}mm{direction_note}{extra_note}, got {{actual}}mm."
    })
    if extent == "symmetric":
        queries.append({
            "id": "q_symmetric", "category": "D_health", "intent": "symmetric_about_plane",
            "expected": True, "tolerance": None,
            "source_field": "(implicit: design_plan specifies symmetric extrude)",
            "feedback_enabled": True,
            "feedback_template": "Body is not symmetric about sketch plane (centroid not on plane). got {actual}."
        })
    queries.append({
        "id": "q_is_solid", "category": "D_health", "intent": "is_solid",
        "expected": True,
        "source_field": "(implicit: valid extrude implies solid)",
        "feedback_enabled": True,
        "feedback_template": "Body is not a closed solid. got {actual}."
    })
    queries.append({
        "id": "q_occt_valid", "category": "D_health", "intent": "occt_valid",
        "expected": True, "source_field": "(implicit)",
        "feedback_enabled": True,
        "feedback_template": "OCCT validation failed. got {actual}."
    })


for sid, ptype, p in SAMPLES:
    queries = [{
        "id": "q_body_count", "category": "A_topology", "intent": "body_count",
        "expected": 1, "source_field": "$.target.body_count",
        "feedback_enabled": True,
        "feedback_template": "Expected body_count=1, got {actual}."
    }]

    if ptype == "rectangle":
        add_bbox(queries, "u", p["lu"], "$.solid_bodies[0].dimensions.profiles[0].length_u.value")
        add_bbox(queries, "v", p["wv"], "$.solid_bodies[0].dimensions.profiles[0].width_v.value")
    elif ptype == "circle":
        r = p["radius"]
        add_bbox(queries, "u", 2 * r, "$.solid_bodies[0].dimensions.profiles[0].radius.value (computed: 2*r)")
        add_bbox(queries, "v", 2 * r, "$.solid_bodies[0].dimensions.profiles[0].radius.value (computed: 2*r)")
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
        add_bbox(queries, "u", 2 * ro, "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value (computed: 2*r)")
        add_bbox(queries, "v", 2 * ro, "$.solid_bodies[0].dimensions.profiles[0].outer_radius.value (computed: 2*r)")
    elif ptype == "stadium":
        sl, r = p["sl"], p["r"]
        add_bbox(queries, "u", sl + 2 * r,
                 "$.solid_bodies[0].dimensions.profiles[0].straight_length.value + .radius.value (computed: straight + 2*r)")
        add_bbox(queries, "v", 2 * r,
                 "$.solid_bodies[0].dimensions.profiles[0].radius.value (computed: 2*r)")
    # arbitrary_closed: only bbox_w + health (no in-plane traceable)

    voids = p.get("voids", 0)
    if voids:
        queries.append({
            "id": "q_void_count", "category": "C_feature", "intent": "through_void_count",
            "expected": voids, "tolerance": 0,
            "source_field": "$.solid_bodies[0].profiles[0].rings[*].role=='inner' count",
            "feedback_enabled": True,
            "feedback_template": f"Expected {voids} through-void(s), got {{actual}}."
        })

    add_health(queries, p.get("dir", "+w"), p.get("extent", "one_side"), p.get("dist", 0))

    instance = {
        "schema_version": "kqp_instance_v0.2",
        "instance_id": f"kqp_{sid}",
        "design_plan_id": sid,
        "step_file": f"data/sanity_set_50/{sid}.step",
        "queries": queries
    }
    out = KQP_DIR / f"{sid}.kqp_instance.json"
    out.write_text(json.dumps(instance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote v0.2: {sid} ({ptype}, extent={p.get('extent','one_side')}, {len(queries)} queries)")
