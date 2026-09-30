"""Reconstruction code for Component5.

Auto-generated from modeling history JSON. Uses cadquery for stable
face+prism construction. NO GT STEP used.

Extent: OneSide, total=168.0 cm = 1680.0 mm (unit conversion cm->mm)
Loops: 2 (1 outer + 1 inner)
"""
import json
import math
from pathlib import Path
import cadquery as cq
from cadquery import exporters

HISTORY_JSON = r"D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究/task5_negative_perturbation/perturbations/101817_b02acd9f_0002/neg_01/perturbed_history.json"
EXTENT_TOTAL_MM = 1680.0
NORMAL = [1.0, 0.0, 0.0]
LOOPS = [{'role': 'inner', 'curves': [{'type': 'line', 'start': (-60.0, 110.0), 'end': (-20.0, 110.0)}, {'type': 'line', 'start': (-60.0, 150.0), 'end': (-60.0, 110.0)}, {'type': 'line', 'start': (-20.0, 150.0), 'end': (-60.0, 150.0)}, {'type': 'line', 'start': (-20.0, 110.0), 'end': (-20.0, 150.0)}]}, {'role': 'outer', 'curves': [{'type': 'line', 'start': (-18.799999999999997, 108.80000000000001), 'end': (-18.799999999999997, 151.2)}, {'type': 'line', 'start': (-18.799999999999997, 151.2), 'end': (-61.2, 151.2)}, {'type': 'line', 'start': (-61.2, 151.2), 'end': (-61.2, 108.80000000000001)}, {'type': 'line', 'start': (-61.2, 108.80000000000001), 'end': (-18.799999999999997, 108.80000000000001)}]}]
WORKPLANE = 'YZ'
OUT_STEP = r"REPLACE_ME_STEP_PATH"


def build_loop_wp(loop_def, is_outer, base_wp):
    """Add a loop's wire to a Workplane. Returns the modified workplane."""
    curves = loop_def["curves"]
    if not curves:
        return base_wp
    # Rectangle: 4 lines, axis-aligned
    if (all(c.get("type") == "line" for c in curves) and len(curves) == 4 and is_outer):
        xs = [c["start"][0] for c in curves] + [c["end"][0] for c in curves]
        ys = [c["start"][1] for c in curves] + [c["end"][1] for c in curves]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        w = xmax - xmin
        h = ymax - ymin
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        return base_wp.moveTo(cx, cy).rect(w, h, centered=True)
    # Single circle
    if len(curves) == 1 and curves[0].get("type") == "circle":
        cx, cy = curves[0]["center"]
        r = curves[0]["radius"]
        return base_wp.moveTo(cx, cy).circle(r)
    # Polyline (multiple lines)
    if all(c.get("type") == "line" for c in curves):
        wp = base_wp.moveTo(curves[0]["start"][0], curves[0]["start"][1])
        for cd in curves:
            wp = wp.lineTo(cd["end"][0], cd["end"][1])
        wp = wp.close()
        return wp
    # Polyline with arcs (stadium, polygon_with_fillets, etc.)
    if is_outer:
        # We split the path into segments. Lines use lineTo. Arcs are
        # discretized into small polyline segments (N=24 by default) to
        # avoid cadquery's radiusArc numerical edge cases (radius not
        # large enough to reach the end point).
        N_ARC = 128
        wp = base_wp
        for i, cd in enumerate(curves):
            if cd.get("type") == "line":
                if i == 0:
                    wp = wp.moveTo(cd["start"][0], cd["start"][1])
                wp = wp.lineTo(cd["end"][0], cd["end"][1])
            elif cd.get("type") == "arc":
                cx, cy = cd["center"]
                r = cd["radius"]
                sa = cd["start_angle"]
                ea = cd["end_angle"]
                # Discretize the arc into N segments
                if i == 0:
                    p1x = cx + r * math.cos(sa)
                    p1y = cy + r * math.sin(sa)
                    wp = wp.moveTo(p1x, p1y)
                for k in range(1, N_ARC + 1):
                    t = sa + (ea - sa) * (k / N_ARC)
                    px = cx + r * math.cos(t)
                    py = cy + r * math.sin(t)
                    wp = wp.lineTo(px, py)
        wp = wp.close()
        return wp
    return base_wp


def main():
    with open(HISTORY_JSON, encoding="utf-8") as f:
        history = json.load(f)

    base_wp = cq.Workplane(WORKPLANE)
    outer_loops = [L for L in LOOPS if L["role"] == "outer"]
    inner_loops = [L for L in LOOPS if L["role"] == "inner"]
    assert outer_loops, "no outer loop"

    # For multi-profile bodies (multiple outer loops): union each outer loop
    # separately, then subtract the corresponding inner loops.
    if len(outer_loops) > 1:
        # Build each outer as its own solid, then union
        results = []
        for o_idx, od in enumerate(outer_loops):
            wp = build_loop_wp(od, True, base_wp.moveTo(0, 0))
            # Find inner loops that belong to this outer (by their curve references
            # but for simplicity, just pair up by index)
            for idl in inner_loops:
                wp = build_loop_wp(idl, False, wp)
            nx, ny, nz = NORMAL
            ext = EXTENT_TOTAL
            if nz < 0 and WORKPLANE == "XY":
                ext = -ext
            results.append(wp.extrude(ext))
        # Union all bodies
        from cadquery import Assembly, Color, Location
        asm = Assembly()
        for r in results:
            asm.add(r, name="b")
        from cadquery import exporters as exp
        exp.export(asm.toCompound(), OUT_STEP)
        return

    base_wp = base_wp.moveTo(0, 0)
    wp = build_loop_wp(outer_loops[0], True, base_wp)

    nx, ny, nz = NORMAL
    ext = EXTENT_TOTAL_MM
    if nz < 0 and WORKPLANE == "XY":
        ext = -ext

    result = wp.extrude(ext)

    # Cut inner holes. For each inner loop, build a cutting prism from
    # the inner wire and subtract. We use a generously-sized cutting prism
    # (overshoot by 50% in extrusion direction) to ensure clean cut.
    for idl in inner_loops:
        cut_wp = build_loop_wp(idl, False, base_wp.moveTo(0, 0))
        # The cutting prism should extend past the body in extrusion direction.
        # Sign: if ext > 0, cut_prism goes +Z (cutting from body bottom up).
        #       if ext < 0, cut_prism goes -Z.
        # We always extrude +Z (away from the sketch plane) and let
        # "result.cut" subtract the volume overlap.
        cut_prism = cut_wp.extrude(abs(ext) * 1.5)
        result = result.cut(cut_prism)

    exporters.export(result, OUT_STEP)


if __name__ == "__main__":
    main()
