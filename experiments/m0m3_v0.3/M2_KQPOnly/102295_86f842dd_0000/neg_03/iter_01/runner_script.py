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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_03\iter_01/generated.step"

    # Design Plan: extruded stadium
    # Profile: stadium shape with straight_length=28.0 mm, radius=10.0 mm
    # Extrude: 4.0 mm in +w direction (which is +Y in world)
    # The stadium is defined in the XZ plane (u=x, v=z, w=y)
    # Dimensions: straight_length=28.0, radius=10.0
    # Total width = 2*radius + straight_length = 20 + 28 = 48.0
    # Height = 2*radius = 20.0
    # Center at origin: left arc center at (-14, 0), right arc center at (14, 0)

    radius = 10.0
    straight_length = 28.0
    half_straight = straight_length / 2.0

    # Build stadium profile in XZ plane using proper cadquery arc and line operations
    wp = cq.Workplane("XZ")

    # Start at left end of top line: (-half_straight, radius)
    # Go clockwise: top line from left to right, right arc (top to bottom), bottom line right to left, left arc (bottom to top)
    # Use threePointArc for proper arcs

    # Build the stadium as a closed wire using cadquery's built-in arc and line methods
    # Start at the left end of the top line
    s = wp.moveTo(-half_straight, radius)

    # Top line from left to right
    s = s.lineTo(half_straight, radius)

    # Right arc: from (half_straight, radius) to (half_straight, -radius) with center at (half_straight, 0)
    # Use threePointArc: start point is current position, end point is (half_straight, -radius), mid point is (half_straight + radius, 0)
    s = s.threePointArc((half_straight + radius, 0), (half_straight, -radius))

    # Bottom line from right to left
    s = s.lineTo(-half_straight, -radius)

    # Left arc: from (-half_straight, -radius) to (-half_straight, radius) with center at (-half_straight, 0)
    # Use threePointArc: start point is current position, end point is (-half_straight, radius), mid point is (-half_straight - radius, 0)
    s = s.threePointArc((-half_straight - radius, 0), (-half_straight, radius))

    # Close the wire
    s = s.close()

    # Extrude in +Y direction (w direction) by 4.0 mm
    result = s.extrude(4.0)

    # Export
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
