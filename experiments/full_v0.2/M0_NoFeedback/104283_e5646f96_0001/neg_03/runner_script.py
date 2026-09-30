import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Extruded profile with a circular hole
    # The profile consists of an outer shape (rectangle with rounded corners approximated by a circle) and an inner circle (hole).
    # Based on the curves:
    #   Outer: vertical line at u=0.9188 from v=1.7937 to v=0, horizontal line from u=0.9188 to u=3.8000 at v=0,
    #          vertical line at u=3.7174 from v=0 to v=1.7937, and a circle centered at (2.3181, 1.7491) radius 1.4.
    #   Inner: circle centered at (2.3181, 1.7491) radius 1.25.
    # Extrude distance: 18.0 mm in +w direction.

    # Note: The coordinates are in mm (converted from cm).

    # Build the outer profile using a combination of lines and an arc (circle segment).
    # The outer ring is a closed loop: start at (0.9188, 1.7937), line down to (0.9188, 0.0),
    # line right to (3.8000, 0.0), line up to (3.7174, 1.7937), then arc (circle) back to start.
    # However, the circle center is at (2.3181, 1.7491) radius 1.4, which connects the two vertical lines.
    # We'll construct the outer wire manually.

    # Points for the outer loop:
    p1 = (0.9188335453558412, 1.7936743887554851)
    p2 = (0.9188335453558412, 0.0)
    p3 = (3.8000000566244125, 0.0)
    p4 = (3.7174115708793822, 1.7936743887554851)
    center = (2.3181225581176115, 1.7490620724718653)
    radius_outer = 1.4
    radius_inner = 1.2500000000000002

    # Create the outer wire:
    # We'll use a Workplane and build the profile.
    # Since the outer shape is not a simple rectangle, we'll use a polygon-like approach with lines and an arc.
    # The arc from p4 to p1 around center.

    # Build the outer face:
    outer_wire = (
        cq.Workplane("XY")
        .moveTo(p1[0], p1[1])
        .lineTo(p2[0], p2[1])
        .lineTo(p3[0], p3[1])
        .lineTo(p4[0], p4[1])
        .threePointArc((center[0] + radius_outer, center[1]), p1)  # arc from p4 to p1 through a point on the circle
        .close()
        .wire()
    )

    # Actually, threePointArc requires three points: start, middle, end.
    # Start is p4, end is p1, middle is a point on the circle.
    # Compute a point on the circle at angle halfway between p4 and p1 relative to center.
    import math
    # Angle of p4 relative to center:
    angle_p4 = math.atan2(p4[1] - center[1], p4[0] - center[0])
    angle_p1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
    # Ensure we go the shorter way (counterclockwise from p4 to p1?)
    # The arc should go from p4 to p1 along the circle. Let's compute midpoint angle.
    mid_angle = (angle_p4 + angle_p1) / 2.0
    mid_point = (center[0] + radius_outer * math.cos(mid_angle), center[1] + radius_outer * math.sin(mid_angle))

    # Rebuild outer wire with proper arc:
    outer_wire = (
        cq.Workplane("XY")
        .moveTo(p1[0], p1[1])
        .lineTo(p2[0], p2[1])
        .lineTo(p3[0], p3[1])
        .lineTo(p4[0], p4[1])
        .threePointArc(mid_point, p1)
        .close()
        .wire()
    )

    # Create inner circle wire:
    inner_circle = cq.Workplane("XY").circle(radius_inner).wire()

    # Build the face with a hole:
    # We need to create a planar face from the outer wire and subtract the inner circle.
    # Use cq.Face.makeFromWires(outer_wire, [inner_circle])
    outer_face = cq.Face.makeFromWires(outer_wire, [inner_circle])

    # Extrude the face by 18.0 mm in the +Z direction (w direction)
    result = outer_face.extrude(18.0)

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0001\\neg_03/generated.step")

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
