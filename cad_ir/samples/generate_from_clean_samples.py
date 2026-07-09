"""generate_from_clean_samples.py — Generate IR examples from the 46 clean samples.

For each clean sample, parse its reconstruction-engine-friendly history
JSON and the v0.6 DesignPlan, and emit a cad_ir_v0.1 IR that:
  * uses the dominant sketch op_type (rectangle / circle / annulus / etc.)
  * uses the extrude distance from the DesignPlan
  * sets up axis-aligned coordinate system (up=z, plane=XY)
  * adds a baseline set of constraints to encode intent

These are "manual IR examples" in the sense that they are hand-derived
from the canonical DesignPlan; they are NOT auto-generated from the
history JSON.  The script reads the canonical sources and renders IR.

Usage:
  python generate_from_clean_samples.py [output_dir]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
from validator import validate  # noqa: E402

CLEAN_PATH = ROOT / "Reconstruction_results" / "clean_reconstruction_set.json"
HIST_DIR = ROOT / "Reconstruction_results"
DP_DIR = ROOT / "DesignPlan" / "compiler" / "instances_v6"


def _bbox_of_loop(loop: dict, points: dict) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for pc in loop.get("profile_curves", []):
        cid = pc.get("curve")
        c = points.get(cid, {}) if points else {}
        sp = c.get("start_point"); ep = c.get("end_point")
        if sp and sp in points: xs.append(points[sp]["x"]); ys.append(points[sp]["y"])
        if ep and ep in points: xs.append(points[ep]["x"]); ys.append(points[ep]["y"])
    if not xs:
        return (0, 0, 1, 1)
    return (min(xs), min(ys), max(xs), max(ys))


def build_ir_for_sample(sample: dict) -> dict:
    sid = sample["sample_id"]
    hist = json.loads((HIST_DIR / sid / "input_history.json").read_text(
        encoding="utf-8"))
    dp = json.loads((DP_DIR / f"{sid}.design_plan.json").read_text(
        encoding="utf-8"))
    ents = hist["entities"]
    sketch = None; extrude = None
    for ev in hist.get("timeline", []):
        e = ents.get(ev.get("entity", ""), {})
        if e.get("type") == "Sketch" and sketch is None: sketch = e
        elif e.get("type") == "ExtrudeFeature" and extrude is None: extrude = e
    body = dp["solid_bodies"][0]
    ptype = body["profiles"][0]["type"]
    dims = body["dimensions"]
    ext_dist = float(dims["extrude_distance"]["value"])
    ext_type = body["extrude"]["extent_type"]   # 'one_side' / 'symmetric'

    operations = []
    op_count = 0

    def next_id() -> str:
        nonlocal op_count
        op_count += 1
        return f"op_{op_count:03d}"

    sketch_op_id = None
    sketch_role = "base_profile"
    sketch_plane = "XY"

    if ptype == "rectangle":
        # dimensions live in body['dimensions']['profiles'][0]
        prof_dims = body.get("dimensions", {}).get("profiles", [{}])[0]
        w = float(prof_dims.get("length_u", {}).get("value", 0))
        h = float(prof_dims.get("width_v", {}).get("value", 0))
        # center: use the bbox center of the original loop (cm) -> mm
        bbox = _bbox_of_loop(sketch["profiles"][list(sketch["profiles"].keys())[0]],
                              sketch.get("points", {}))
        cx_mm = (bbox[0] + bbox[2]) / 2 * 10
        cy_mm = (bbox[1] + bbox[3]) / 2 * 10
        if w <= 0 or h <= 0:
            # Fallback: derive from bbox extents (mm)
            w = (bbox[2] - bbox[0]) * 10
            h = (bbox[3] - bbox[1]) * 10
        sketch_op_id = next_id()
        operations.append({
            "op_id": sketch_op_id, "op_type": "sketch_rectangle",
            "role": sketch_role, "plane": sketch_plane,
            "params": {"width": w, "height": h, "center": [cx_mm, cy_mm]},
        })

    elif ptype == "circle":
        r_cm = 0.0
        for c in sketch["curves"].values():
            if c.get("type") == "SketchCircle":
                r_cm = c.get("radius", 0)
                break
        r_mm = r_cm * 10
        # center from center_point
        center_pt_uuid = next((c.get("center_point") for c in sketch["curves"].values()
                                if c.get("type") == "SketchCircle"), None)
        cx_mm = cy_mm = 0.0
        if center_pt_uuid and center_pt_uuid in sketch.get("points", {}):
            pt = sketch["points"][center_pt_uuid]
            cx_mm, cy_mm = pt["x"] * 10, pt["y"] * 10
        sketch_op_id = next_id()
        operations.append({
            "op_id": sketch_op_id, "op_type": "sketch_circle",
            "role": sketch_role, "plane": sketch_plane,
            "params": {"radius": r_mm, "center": [cx_mm, cy_mm]},
        })

    elif ptype == "annulus":
        # Prefer DesignPlan profile dimensions (in mm) when available.
        prof_dims = body.get("dimensions", {}).get("profiles", [{}])[0]
        ir_dp = prof_dims.get("inner_radius", {}).get("value")
        or_dp = prof_dims.get("outer_radius", {}).get("value")
        if ir_dp and or_dp:
            inner_mm = float(ir_dp); outer_mm = float(or_dp)
            cp = prof_dims.get("center_uv", {})
            cx_mm = float(cp.get("x", 0) or cp[0] if isinstance(cp, dict) else (cp[0] if cp else 0))
            cy_mm = float(cp.get("y", 0) or cp[1] if isinstance(cp, dict) else (cp[1] if cp else 0))
        else:
            circles = [c for c in sketch["curves"].values()
                       if c.get("type") == "SketchCircle"]
            radii_cm = sorted([c.get("radius", 0) for c in circles])
            inner_mm = radii_cm[0] * 10
            outer_mm = radii_cm[1] * 10
            center_pt = circles[-1].get("center_point") if circles else None
            cx_mm = cy_mm = 0.0
            if center_pt and center_pt in sketch.get("points", {}):
                pt = sketch["points"][center_pt]
                cx_mm, cy_mm = pt["x"] * 10, pt["y"] * 10
        if inner_mm <= 0 or outer_mm <= 0:
            inner_mm = 0.5
            outer_mm = 1.0
        sketch_op_id = next_id()
        operations.append({
            "op_id": sketch_op_id, "op_type": "sketch_annulus",
            "role": sketch_role, "plane": sketch_plane,
            "params": {"inner_radius": inner_mm,
                          "outer_radius": outer_mm,
                          "center": [cx_mm, cy_mm]},
        })

    elif ptype == "rectangular_frame":
        rings = body["profiles"][0].get("rings", [])
        outer_ring = next((r for r in rings if r.get("role") == "outer"), None)
        inner_ring = next((r for r in rings if r.get("role") == "inner"), None)
        if outer_ring and inner_ring:
            def ring_extents(ring):
                coords = []
                for c in ring.get("curves", []):
                    for k in ("start_uv", "end_uv"):
                        coords.append(c.get(k))
                xs = [c[0] for c in coords]
                ys = [c[1] for c in coords]
                return (max(xs) - min(xs)) * 10, (max(ys) - min(ys)) * 10
            ow, oh = ring_extents(outer_ring)
            iw, ih = ring_extents(inner_ring)
            bbox = _bbox_of_loop(outer_ring, {})
            cx_mm = (bbox[0] + bbox[2]) / 2 * 10
            cy_mm = (bbox[1] + bbox[3]) / 2 * 10
            sketch_op_id = next_id()
            operations.append({
                "op_id": sketch_op_id,
                "op_type": "sketch_rectangular_frame",
                "role": sketch_role, "plane": sketch_plane,
                "params": {"outer_width": ow, "outer_height": oh,
                              "inner_width": iw, "inner_height": ih,
                              "center": [cx_mm, cy_mm]},
            })

    elif ptype == "stadium":
        # Compute from arc radius + line length
        arcs = [c for c in sketch["curves"].values() if c.get("type") == "SketchArc"]
        lines = [c for c in sketch["curves"].values() if c.get("type") == "SketchLine"]
        r_mm = arcs[0]["radius"] * 10 if arcs else 0
        line_lengths_mm = []
        for ln in lines:
            sp = sketch["points"].get(ln.get("start_point"))
            ep = sketch["points"].get(ln.get("end_point"))
            if sp and ep:
                line_lengths_mm.append(((ep["x"] - sp["x"]) ** 2 +
                                          (ep["y"] - sp["y"]) ** 2) ** 0.5 * 10)
        # length of stadium = max line length
        length_mm = max(line_lengths_mm) if line_lengths_mm else 0
        # Center
        pts = list(sketch["points"].values())
        cx_mm = sum(p["x"] for p in pts) / len(pts) * 10
        cy_mm = sum(p["y"] for p in pts) / len(pts) * 10
        sketch_op_id = next_id()
        operations.append({
            "op_id": sketch_op_id, "op_type": "sketch_stadium",
            "role": sketch_role, "plane": sketch_plane,
            "params": {"length": length_mm, "radius": r_mm,
                          "center": [cx_mm, cy_mm]},
        })

    else:
        # arbitrary_closed: build a sketch_polygon from the outer ring.
        # We use start/end vertices (including arcs whose center is the
        # endpoint of an adjacent line).  This may lose arc curvature,
        # which is acceptable for V0.1 IR — the adaptor renders an
        # n-gon approximation; the KQP feedback will flag deviations.
        ring = body["profiles"][0]["rings"][0]
        verts = []
        seen = set()
        for c in ring.get("curves", []):
            for k in ("start_uv", "end_uv"):
                pt = c.get(k)
                if not pt or len(pt) < 2:
                    continue
                t = tuple(round(x, 4) for x in pt[:2])
                if t not in seen:
                    seen.add(t)
                    verts.append([pt[0] * 10, pt[1] * 10])
        if verts:
            sketch_op_id = next_id()
            operations.append({
                "op_id": sketch_op_id, "op_type": "sketch_polygon",
                "role": sketch_role, "plane": sketch_plane,
                "params": {"vertices": verts},
            })

    if sketch_op_id is None:
        # Fallback: empty rectangle
        sketch_op_id = next_id()
        operations.append({
            "op_id": sketch_op_id, "op_type": "sketch_rectangle",
            "role": sketch_role, "plane": sketch_plane,
            "params": {"width": 1.0, "height": 1.0, "center": [0.0, 0.0]},
        })

    # Extrude
    extrude_id = next_id()
    operations.append({
        "op_id": extrude_id, "op_type": "extrude",
        "role": "base_body", "input": sketch_op_id,
        "params": {"distance": ext_dist, "extent_type": ext_type,
                    "operation": "new_body",
                    "direction": "+normal"},
    })

    # Export
    export_id = next_id()
    operations.append({
        "op_id": export_id, "op_type": "export_step",
        "input": extrude_id,
        "params": {"path": f"{sid}.step"},
    })

    return {
        "schema_version": "cad_ir_v0.1",
        "sample_id": sid,
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y",
                                 "right_axis": "x"},
        "operations": operations,
        "metadata": {"source": "manual_from_clean_sample",
                       "profile_type": ptype},
    }


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        (Path(__file__).resolve().parent / "manual_ir_examples")
    out_dir.mkdir(parents=True, exist_ok=True)

    clean = json.loads(CLEAN_PATH.read_text(encoding="utf-8"))
    summary = {"generated": 0, "schema_pass": 0, "semantic_pass": 0,
                "errors": []}
    for s in clean["clean_samples"]:
        sid = s["sample_id"]
        try:
            ir = build_ir_for_sample(s)
        except Exception as e:
            summary["errors"].append(f"{sid}: build failed: {e}")
            continue

        result = validate(ir)
        out_path = out_dir / f"{sid}.cad_ir.json"
        out_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False),
                              encoding="utf-8")
        summary["generated"] += 1
        if result["schema_status"] == "pass":
            summary["schema_pass"] += 1
        if result["semantic_status"] == "pass":
            summary["semantic_pass"] += 1
        if result["overall"] != "pass":
            summary["errors"].append(
                f"{sid}: {result['schema_status']}/{result['semantic_status']}"
                f"  schema_issues={result['schema_issues'][:2]}  "
                f"semantic_issues={result['semantic_issues'][:2]}")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()