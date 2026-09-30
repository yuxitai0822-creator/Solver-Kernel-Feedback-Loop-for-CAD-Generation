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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0001\neg_01\iter_01\generated.step"

    # Design Plan interpretation:
    # - Two profiles: first is a closed shape with 4 curves (3 lines + 1 circle), second is a ring (outer circle + inner circle)
    # - Extrude distance: 18.0 mm (from design plan)
    # - The first profile creates a base shape, the second creates a through hole

    # Profile 1: Arbitrary closed shape with 3 lines and 1 circle
    # Curves:
    # 1. Line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
    # 2. Line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
    # 3. Line from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
    # 4. Circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.4

    # Profile 2: Ring shape
    # Outer: Circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.4
    # Inner: Circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.25

    # Note: The coordinates in the design plan are in cm (unit_conversion_applied: cm_to_mm x10)
    # So we multiply all coordinates by 10 to get mm
    SCALE = 10.0

    # Profile 1 coordinates (scaled to mm)
    p1_line1_start = (0.9188335453558412 * SCALE, 1.7936743887554851 * SCALE)
    p1_line1_end = (0.9188335453558412 * SCALE, 0.0)
    p1_line2_start = (0.9188335453558412 * SCALE, 0.0)
    p1_line2_end = (3.8000000566244125 * SCALE, 0.0)
    p1_line3_start = (3.7174115708793822 * SCALE, 1.7936743887554851 * SCALE)
    p1_line3_end = (3.7174115708793822 * SCALE, 0.0)
    p1_circle_center = (2.3181225581176115 * SCALE, 1.7490620724718653 * SCALE)
    p1_circle_radius = 1.4 * SCALE

    # Profile 2 coordinates (scaled to mm)
    p2_outer_center = (2.3181225581176115 * SCALE, 1.7490620724718653 * SCALE)
    p2_outer_radius = 1.4 * SCALE
    p2_inner_radius = 1.2500000000000002 * SCALE

    # Extrude distance from design plan: 18.0 mm
    extrude_distance = 18.0

    # Build the first profile (base shape)
    # The profile consists of 3 lines and 1 circle forming a closed loop
    # We'll build it as a wire and then extrude it

    # Create the workplane
    wp = cq.Workplane("XY")

    # Build the first profile using polyline and circle
    # Start at the first point
    p = cq.Vector(p1_line1_start[0], p1_line1_start[1])

    # Create the base shape by extruding the first profile
    # We'll use a combination of operations

    # First, create the outer shape of profile 1 (the 3 lines + circle)
    # The circle is at the top, so we need to create a shape that includes it

    # Approach: Create a rectangle that covers the bounding box, then cut out the circle area
    # Actually, let's build the profile as a wire

    # Points for the polyline (excluding the circle part)
    pts = [
        (p1_line1_start[0], p1_line1_start[1]),  # top-left
        (p1_line1_end[0], p1_line1_end[1]),      # bottom-left
        (p1_line2_end[0], p1_line2_end[1]),      # bottom-right
        (p1_line3_end[0], p1_line3_end[1]),      # bottom-right (same as above? No, line3_end is different)
    ]

    # Actually, let's re-examine the curves:
    # Curve 1: line from (0.9188, 1.7937) to (0.9188, 0.0)  -- left vertical line
    # Curve 2: line from (0.9188, 0.0) to (3.8000, 0.0)     -- bottom horizontal line
    # Curve 3: line from (3.7174, 1.7937) to (3.7174, 0.0)  -- right vertical line (going down)
    # Curve 4: circle centered at (2.3181, 1.7491) radius 1.4 -- top arc

    # So the shape is like a rectangle with a circular top
    # The circle connects the top-left and top-right points

    # Let's build this as a proper closed wire

    # Create points for the polyline part
    poly_pts = [
        (p1_line1_start[0], p1_line1_start[1]),  # start at top-left
        (p1_line1_end[0], p1_line1_end[1]),      # go down to bottom-left
        (p1_line2_end[0], p1_line2_end[1]),      # go right to bottom-right
        (p1_line3_end[0], p1_line3_end[1]),      # go up to bottom of right line
    ]

    # Build the wire
    wire = cq.Workplane("XY")
    wire = wire.moveTo(poly_pts[0][0], poly_pts[0][1])
    for pt in poly_pts[1:]:
        wire = wire.lineTo(pt[0], pt[1])

    # Now add the circle arc from top-right to top-left
    # The circle center is at p1_circle_center, radius p1_circle_radius
    # We need to find the angles from center to the two points
    cx, cy = p1_circle_center
    r = p1_circle_radius

    # Top-left point: (0.9188, 1.7937)
    # Top-right point: (3.7174, 1.7937)
    # But wait, the circle connects these two points

    # Let's compute the angles
    import math

    # Point on circle at top-left
    p_tl = cq.Vector(p1_line1_start[0], p1_line1_start[1])
    p_tr = cq.Vector(p1_line3_start[0], p1_line3_start[1])  # This is the top-right point

    # Compute angles from circle center
    angle_tl = math.atan2(p_tl.y - cy, p_tl.x - cx)
    angle_tr = math.atan2(p_tr.y - cy, p_tr.x - cx)

    # The arc goes from angle_tr to angle_tl (counterclockwise)
    # We need to determine the correct direction
    # Since the circle is at the top, the arc should go from right to left (counterclockwise)
    # So start at angle_tr, end at angle_tl

    # Add the arc
    wire = wire.threePointArc(
        cq.Vector(cx + r * math.cos((angle_tr + angle_tl) / 2), cy + r * math.sin((angle_tr + angle_tl) / 2)),
        p_tl
    )

    # Close the wire
    wire = wire.close()

    # Extrude the first profile
    result = wire.extrude(extrude_distance)

    # Now create the second profile (ring) and cut it from the result
    # The ring is centered at p2_outer_center with outer radius p2_outer_radius and inner radius p2_inner_radius

    # Create the outer circle of the ring
    outer_circle = cq.Workplane("XY").moveTo(p2_outer_center[0], p2_outer_center[1]).circle(p2_outer_radius)

    # Create the inner circle of the ring
    inner_circle = cq.Workplane("XY").moveTo(p2_outer_center[0], p2_outer_center[1]).circle(p2_inner_radius)

    # Create the ring by extruding the outer circle and cutting the inner circle
    ring = outer_circle.extrude(extrude_distance)
    ring = ring.cut(inner_circle.extrude(extrude_distance))

    # Cut the ring from the result (this creates the through hole)
    result = result.cut(ring)

    # Export
    import os
    os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
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
