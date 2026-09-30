import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math
    from cadquery import exporters

    # Design Plan: ArmRest v1 - stadium extrusion
    # Stadium profile: straight length 500mm, radius 50mm (original 5.0 -> perturbed to 6.25? 
    # But design plan says radius=50.0, straight_length=500.0. The perturbation description says 
    # E3_radius; original=5.0; perturbed=6.25 but that seems inconsistent with the dimensions.
    # We follow the design plan dimensions: straight_length=500.0, radius=50.0, extrude=100.0

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_02\iter_00/generated.step"

    # Build stadium profile
    # The stadium consists of:
    # - Arc at left end: center (0,0), radius 50, from 0 to 180 degrees (top to bottom)
    # - Bottom line: from (0, -50) to (500, -50)
    # - Arc at right end: center (500,0), radius 50, from 0 to 180 degrees (bottom to top)
    # - Top line: from (500, 50) to (0, 50)

    # Create the stadium profile using CadQuery's 2D construction
    wp = cq.Workplane("XY")

    # Build the stadium shape using polyline with arcs discretized
    # Start at left arc top: (0, 50)
    # Arc left: center (0,0), radius 50, from 90 to -90 degrees (top to bottom)
    # Line bottom: (0, -50) to (500, -50)
    # Arc right: center (500,0), radius 50, from -90 to 90 degrees (bottom to top)
    # Line top: (500, 50) to (0, 50)

    # Use a high-resolution discretization for arcs
    N = 64

    # Build the wire manually
    pts = []

    # Left arc (top to bottom)
    for i in range(N + 1):
        angle = math.pi/2 - math.pi * i / N  # from 90 to -90 degrees
        x = 0 + 50 * math.cos(angle)
        y = 0 + 50 * math.sin(angle)
        pts.append((x, y))

    # Bottom line (already at (0, -50) to (500, -50))
    # The last point of arc is (0, -50), so we add intermediate points for the line
    for i in range(1, N + 1):
        x = 500 * i / N
        y = -50
        pts.append((x, y))

    # Right arc (bottom to top)
    for i in range(N + 1):
        angle = -math.pi/2 + math.pi * i / N  # from -90 to 90 degrees
        x = 500 + 50 * math.cos(angle)
        y = 0 + 50 * math.sin(angle)
        pts.append((x, y))

    # Top line (already at (500, 50) to (0, 50))
    for i in range(1, N):
        x = 500 - 500 * i / N
        y = 50
        pts.append((x, y))

    # Build the wire and make a face
    wire = cq.Workplane("XY").polyline(pts).close().extrude(100.0)

    # Alternative: use the simpler approach with CadQuery's built-in shapes
    # Since CadQuery doesn't have a direct stadium shape, we build it from two circles and a rectangle
    wp2 = cq.Workplane("XY")

    # Create left circle at (0,0) radius 50
    left_circle = wp2.moveTo(0, 0).circle(50)

    # Create right circle at (500,0) radius 50
    right_circle = wp2.moveTo(500, 0).circle(50)

    # Create rectangle connecting them: width 500, height 100, centered at (250, 0)
    rect = wp2.moveTo(250, 0).rect(500, 100, centered=True)

    # Combine: union of left circle, right circle, and rectangle
    # Then extrude
    result = left_circle.union(right_circle).union(rect).extrude(100.0)

    # Export
    cq.exporters.export(result, OUT_STEP_PATH)

import cadquery as _cq_auto
_INSTANTIATED_WORKPLANES = []
_orig_wp_init = _cq_auto.Workplane.__init__
def _hooked_wp_init(self, *args, **kwargs):
    _INSTANTIATED_WORKPLANES.append(self)
    return _orig_wp_init(self, *args, **kwargs)
_cq_auto.Workplane.__init__ = _hooked_wp_init

def _export_latest_wp(OUT_STEP_PATH):
    if not _INSTANTIATED_WORKPLANES:
        return False, "no_workplane_created"
    wp = _INSTANTIATED_WORKPLANES[-1]
    try:
        solid_or_compound = wp.val() if hasattr(wp, "val") else wp
        _cq_auto.exporters.export(solid_or_compound, OUT_STEP_PATH)
        return True, "ok"
    except Exception as e:
        return False, f"export_error: {e}"

try:
    _user_main()
    out_path = os.environ.get("OUT_STEP_PATH", "")
    if out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(json.dumps({"status": "ok", "out_step": out_path}))
    else:
        ok, reason = _export_latest_wp(out_path) if out_path else (False, "no_out_path")
        if ok and out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            print(json.dumps({"status": "ok_autoexport", "out_step": out_path}))
        else:
            print(json.dumps({"status": "no_step_written", "out_step": out_path, "autoexport_reason": reason}))
except Exception as e:
    print(json.dumps({"status": "exception",
                       "error": str(e),
                       "traceback": traceback.format_exc()[-500:]}))
