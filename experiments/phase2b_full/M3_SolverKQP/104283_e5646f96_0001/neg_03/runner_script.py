import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Extruded profile with a circular hole
    # The profile consists of an outer shape (rectangle with rounded corners via a circle) and an inner circle (hole).
    # The outer shape is defined by four curves: two vertical lines and two arcs (circles) that form a slot-like shape.
    # Actually, the curves describe a rectangle with a circular end? Let's interpret carefully.
    # Curves:
    # 1. line from (0.9188, 1.7937) to (0.9188, 0.0)  -> left vertical line
    # 2. line from (0.9188, 0.0) to (3.8000, 0.0)      -> bottom horizontal line
    # 3. line from (3.7174, 1.7937) to (3.7174, 0.0)   -> right vertical line
    # 4. circle center (2.3181, 1.7491) radius 1.4     -> top arc connecting the two vertical lines
    # This forms a closed shape: a rectangle with a circular top (like a D-shape or a slot).
    # The second profile has an inner circle (hole) at same center with radius 1.25.
    # Extrude distance: 18.0 mm in +w direction (z-axis).

    # Build the outer profile as a wire
    outer = (
        cq.Workplane("XY")
        .moveTo(0.9188335453558412, 1.7936743887554851)
        .lineTo(0.9188335453558412, 0.0)
        .lineTo(3.8000000566244125, 0.0)
        .lineTo(3.7174115708793822, 0.0)
        .lineTo(3.7174115708793822, 1.7936743887554851)
        .threePointArc(
            (2.3181225581176115, 1.7490620724718653 + 1.4),
            (0.9188335453558412, 1.7936743887554851)
        )
        .close()
    )

    # Actually, the arc is a circle of radius 1.4 centered at (2.3181, 1.7491).
    # The endpoints of the arc are (0.9188, 1.7937) and (3.7174, 1.7937).
    # Let's compute the arc properly: center (2.3181, 1.7491), radius 1.4.
    # The start point (0.9188, 1.7937) and end point (3.7174, 1.7937) are symmetric about the center.
    # We can use threePointArc with a midpoint on the circle.
    # Midpoint angle: from center, the start angle is atan2(1.7937-1.7491, 0.9188-2.3181) = atan2(0.0446, -1.3993) ≈ 178.17°
    # End angle: atan2(1.7937-1.7491, 3.7174-2.3181) = atan2(0.0446, 1.3993) ≈ 1.83°
    # The arc goes the short way (counterclockwise) from start to end, passing through top point (2.3181, 1.7491+1.4) = (2.3181, 3.1491)
    # So midpoint is (2.3181, 3.1491)

    # Let's rebuild more cleanly:
    # We'll create the outer profile as a closed wire using lines and a three-point arc.

    # Start at left top
    p_start = (0.9188335453558412, 1.7936743887554851)
    p_bottom_left = (0.9188335453558412, 0.0)
    p_bottom_right = (3.8000000566244125, 0.0)
    p_right_top = (3.7174115708793822, 1.7936743887554851)
    center = (2.3181225581176115, 1.7490620724718653)
    radius = 1.4
    # Midpoint on the arc (top of circle)
    p_mid = (center[0], center[1] + radius)  # (2.3181, 3.1491)

    outer_wire = (
        cq.Workplane("XY")
        .moveTo(p_start[0], p_start[1])
        .lineTo(p_bottom_left[0], p_bottom_left[1])
        .lineTo(p_bottom_right[0], p_bottom_right[1])
        .lineTo(p_right_top[0], p_right_top[1])
        .threePointArc(p_mid, p_start)
        .close()
    )

    # Now create the inner circle (hole)
    inner_radius = 1.2500000000000002
    inner_center = (2.3181225581176115, 1.7490620724718653)

    # Build the full profile: outer wire with inner hole
    # We can use Workplane to create a face with a hole
    result = (
        cq.Workplane("XY")
        .moveTo(p_start[0], p_start[1])
        .lineTo(p_bottom_left[0], p_bottom_left[1])
        .lineTo(p_bottom_right[0], p_bottom_right[1])
        .lineTo(p_right_top[0], p_right_top[1])
        .threePointArc(p_mid, p_start)
        .close()
        .extrude(18.0)
        .faces(">Z")  # select top face
        .workplane()
        .circle(inner_radius)
        .cutThruAll()
    )

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\104283_e5646f96_0001\neg_03/generated.step")

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
