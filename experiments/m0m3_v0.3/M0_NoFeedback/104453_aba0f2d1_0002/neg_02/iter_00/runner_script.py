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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0002\neg_02\iter_00\generated.step"

    # Build the stadium profile directly using cadquery primitives
    # The design plan specifies:
    # - Straight length: 500.0 mm (distance between arc centers)
    # - Radius: 50.0 mm (arc radius)
    # - Extrude distance: 100.0 mm

    # Note: The perturbation description says radius was changed from 5.0 to 6.25,
    # but the design plan dimensions clearly state radius=50.0 and straight_length=500.0.
    # We follow the design plan dimensions.

    straight_length = 500.0
    radius = 50.0
    extrude_distance = 100.0

    # Create the stadium profile:
    # 1. Start with a rectangle for the straight section
    # 2. Add semicircular ends

    # Using cadquery's 2D construction:
    wp = cq.Workplane("XY")

    # Build the stadium shape:
    # - Two arcs (semicircles) at each end
    # - Two lines connecting them

    # Approach: Create the profile by combining primitives
    # The stadium has total width = straight_length + 2*radius = 600.0
    # Total height = 2*radius = 100.0

    # Create the profile using a polyline with arcs
    # Start at bottom-left of left arc
    p = cq.Workplane("XY")

    # Build the stadium profile point by point
    # Left semicircle (center at 0,0, radius=50)
    # Right semicircle (center at 500,0, radius=50)

    # Use the three-point arc method for better numerical stability
    # Left arc: from (0, -50) to (0, 50) through (50, 0) - wait, that's wrong
    # Left arc: center at (0,0), from angle -90 to +90 (bottom to top)
    # Right arc: center at (500,0), from angle +90 to -90 (top to bottom)

    # Better approach: use cadquery's wire construction
    # Create the stadium as a single closed wire

    # Define points for the stadium profile
    # Start at bottom of left arc: (0, -50)
    # Line to bottom of right arc: (500, -50)
    # Right arc from (500, -50) to (500, 50) with center at (500, 0)
    # Line from (500, 50) to (0, 50)
    # Left arc from (0, 50) to (0, -50) with center at (0, 0)

    # Use cadquery's three-point arc for each semicircle
    # For the right arc: start=(500,-50), mid=(550,0), end=(500,50)
    # For the left arc: start=(0,50), mid=(-50,0), end=(0,-50)

    # Build the profile
    s = (
        cq.Workplane("XY")
        .moveTo(0, -radius)  # Start at bottom of left arc
        .lineTo(straight_length, -radius)  # Bottom line
        .threePointArc(
            (straight_length + radius, 0),  # Mid point of right arc
            (straight_length, radius)  # End of right arc
        )
        .lineTo(0, radius)  # Top line
        .threePointArc(
            (-radius, 0),  # Mid point of left arc
            (0, -radius)  # End of left arc (back to start)
        )
        .close()
    )

    # Extrude the profile
    result = s.extrude(extrude_distance)

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
