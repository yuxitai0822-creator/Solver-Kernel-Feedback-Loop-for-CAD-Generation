import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102295_86f842dd_0000\neg_02\iter_02/generated.step"

    # Design parameters from the plan:
    # Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
    # Extrude distance = 4.0 mm
    # The profile is defined in UV space where:
    #   u_dir = [1,0,0] (X axis)
    #   v_dir = [0,0,-1] (negative Z axis)
    #   w_dir = [0,1,0] (Y axis)
    # So the sketch is in the XZ plane, extruded along Y.

    straight_length = 28.0
    radius = 10.0
    extrude_distance = 4.0

    # Build the stadium profile in the XZ plane (Y=0)
    # The stadium consists of:
    # - Left arc centered at (radius, 0) with radius, from 0 to 180 degrees (top to bottom)
    # - Bottom line from (radius, -radius) to (radius + straight_length, -radius)
    # - Right arc centered at (radius + straight_length, 0) with radius, from 0 to 180 degrees (bottom to top)
    # - Top line from (radius + straight_length, radius) to (radius, radius)

    # Start with a workplane on the XZ plane
    wp = cq.Workplane("XZ")

    # Build the profile using polyline and arc segments
    # We'll use the three-point arc method for better accuracy

    # Start at the top of the left arc: (radius, radius)
    start_x = radius
    start_z = radius

    # Left arc: from top (0 deg) to bottom (180 deg), center at (radius, 0)
    # Points: start (radius, radius), mid (radius + radius, 0), end (radius, -radius)
    left_arc_mid_x = radius + radius
    left_arc_mid_z = 0
    left_arc_end_x = radius
    left_arc_end_z = -radius

    # Bottom line: from (radius, -radius) to (radius + straight_length, -radius)
    bottom_end_x = radius + straight_length
    bottom_end_z = -radius

    # Right arc: from bottom (180 deg) to top (0 deg), center at (radius + straight_length, 0)
    # Points: start (radius + straight_length, -radius), mid (radius + straight_length - radius, 0), end (radius + straight_length, radius)
    right_arc_mid_x = radius + straight_length - radius
    right_arc_mid_z = 0
    right_arc_end_x = radius + straight_length
    right_arc_end_z = radius

    # Top line: from (radius + straight_length, radius) back to (radius, radius)
    top_end_x = radius
    top_end_z = radius

    # Build the wire
    profile = (
        wp.moveTo(start_x, start_z)
        .threePointArc((left_arc_mid_x, left_arc_mid_z), (left_arc_end_x, left_arc_end_z))
        .lineTo(bottom_end_x, bottom_end_z)
        .threePointArc((right_arc_mid_x, right_arc_mid_z), (right_arc_end_x, right_arc_end_z))
        .lineTo(top_end_x, top_end_z)
        .close()
    )

    # Extrude along Y axis (positive direction)
    result = profile.extrude(extrude_distance)

    # Export to STEP
    exporters.export(result, OUT_STEP_PATH)

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
