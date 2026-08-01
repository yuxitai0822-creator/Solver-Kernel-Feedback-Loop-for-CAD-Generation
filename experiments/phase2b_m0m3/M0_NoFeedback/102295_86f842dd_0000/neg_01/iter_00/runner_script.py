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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102295_86f842dd_0000\neg_01\iter_00\generated.step"

    # Design parameters from the design plan
    # Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
    # Extrude distance = 4.0 mm (as per design plan, not the perturbed value)
    straight_length = 28.0
    radius = 10.0
    extrude_distance = 4.0

    # Build the stadium profile in the XZ plane (as per the original script's WORKPLANE = 'XZ')
    # The profile lies in the XZ plane, with extrusion along Y axis
    # Stadium: two semicircles of radius 10.0 connected by straight segments of length 28.0
    # Total width = 2*radius + straight_length = 20.0 + 28.0 = 48.0
    # Total height = 2*radius = 20.0

    # Create workplane on XZ
    wp = cq.Workplane("XZ")

    # Build the stadium profile
    # Start at the left semicircle center: (radius, 0) in XZ plane
    # The profile will be centered at origin
    # Left semicircle: center at (-straight_length/2, 0), radius = radius
    # Right semicircle: center at (straight_length/2, 0), radius = radius

    # Build using polyline and arc segments
    # Start at bottom-left of left semicircle
    center_x = 0.0
    center_z = 0.0
    left_center_x = center_x - straight_length / 2.0
    right_center_x = center_x + straight_length / 2.0

    # Build the profile as a closed wire
    # Start at bottom of left semicircle
    start_x = left_center_x
    start_z = center_z - radius

    # Create the profile using a series of points
    # We'll use the approach of creating a 2D sketch with lines and arcs
    # Using cadquery's built-in methods for a stadium shape

    # Alternative: create the stadium using two circles and two lines, then combine
    # But simpler: use the wire builder with points

    # Create the stadium profile by constructing the outer wire
    # Points for the stadium (going counterclockwise):
    # 1. Bottom-left point of left semicircle
    # 2. Bottom-right point of right semicircle (via bottom line)
    # 3. Top-right point of right semicircle (via right semicircle arc)
    # 4. Top-left point of left semicircle (via top line)
    # 5. Back to 1 (via left semicircle arc)

    # Use cadquery's polygon approach with arc approximation
    # Since cadquery doesn't have a direct stadium primitive, we build it manually

    # Create the profile on the XZ plane
    # We'll use the workplane's 2D drawing capabilities

    # Method: create a closed wire by combining edges
    # Start with the bottom line
    s = cq.Workplane("XZ").moveTo(left_center_x, center_z - radius).lineTo(right_center_x, center_z - radius)

    # Add the right semicircle (arc from bottom to top)
    s = s.threePointArc((right_center_x + radius, center_z), (right_center_x, center_z + radius))

    # Add the top line
    s = s.lineTo(left_center_x, center_z + radius)

    # Add the left semicircle (arc from top to bottom)
    s = s.threePointArc((left_center_x - radius, center_z), (left_center_x, center_z - radius))

    # Close the wire
    s = s.close()

    # Extrude along Y axis (positive direction)
    result = s.extrude(extrude_distance)

    # Export to STEP
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
