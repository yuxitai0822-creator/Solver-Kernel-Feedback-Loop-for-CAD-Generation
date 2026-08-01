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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0001\neg_03\iter_00\generated.step"

    # Design parameters from the design plan (all in mm)
    extrude_distance = 18.0

    # Profile 1: outer ring (composite line-arc)
    # Curves from design plan:
    #   line: (0.9188335453558412, 1.7936743887554851) -> (0.9188335453558412, 0.0)
    #   line: (0.9188335453558412, 0.0) -> (3.8000000566244125, 0.0)
    #   line: (3.7174115708793822, 1.7936743887554851) -> (3.7174115708793822, 0.0)
    #   circle: center (2.3181225581176115, 1.7490620724718653), radius 1.4
    #
    # Profile 2: outer ring (composite line-arc) with inner circle (hole)
    #   circle: center (2.3181225581176115, 1.7490620724718653), radius 1.4
    #   line: (3.7174115708793822, 1.7936743887554851) -> (3.7174115708793822, 0.0)
    #   circle: center (2.3181225581176115, 1.7490620724718653), radius 1.4
    #   line: (0.9188335453558412, 1.7936743887554851) -> (0.9188335453558412, 0.0)
    #   inner circle: center (2.3181225581176115, 1.7490620724718653), radius 1.25

    # The design plan describes two profiles that together form the part.
    # Profile 1 is a closed shape with 4 curves (3 lines + 1 circle arc).
    # Profile 2 is a closed shape with 4 curves (2 circles + 2 lines) and an inner circle.
    # The circles share the same center (concentric constraint).
    # The overall shape is like a rectangular plate with a circular boss on top,
    # and a through hole in the center.

    # Build the base profile (profile 1): a rectangle with a circular arc on top
    # The rectangle goes from x=0.9188 to x=3.8000, y=0 to y=1.7937
    # But the top edge is replaced by a circular arc of radius 1.4 centered at (2.3181, 1.7491)

    # Let's build this as a 2D sketch using cadquery's workplane

    # Create the base workplane
    wp = cq.Workplane("XY")

    # Build the outer profile using polyline and arc
    # Start at bottom-left corner
    p1 = (0.9188335453558412, 0.0)
    p2 = (3.8000000566244125, 0.0)
    p3 = (3.7174115708793822, 1.7936743887554851)
    p4 = (0.9188335453558412, 1.7936743887554851)

    # The circle arc connects p4 to p3 (or p3 to p4) with center at (2.3181225581176115, 1.7490620724718653)
    # Radius = 1.4

    # Build the outer wire manually
    # Start at p1, go to p2, then to p3, then arc to p4, then close back to p1

    # Create points list for the polyline portion
    pts = [p1, p2, p3]

    # Build the wire
    wire = wp.moveTo(p1[0], p1[1]).lineTo(p2[0], p2[1]).lineTo(p3[0], p3[1])

    # Now add the arc from p3 to p4
    # The arc center is at (2.3181225581176115, 1.7490620724718653)
    # We need to compute start and end angles
    cx, cy = 2.3181225581176115, 1.7490620724718653
    r = 1.4

    # Compute angles from center to p3 and p4
    # p3 = (3.7174115708793822, 1.7936743887554851)
    # p4 = (0.9188335453558412, 1.7936743887554851)

    # Angle from center to p3
    dx3 = p3[0] - cx
    dy3 = p3[1] - cy
    angle3 = math.atan2(dy3, dx3)

    # Angle from center to p4
    dx4 = p4[0] - cx
    dy4 = p4[1] - cy
    angle4 = math.atan2(dy4, dx4)

    # The arc goes from p3 to p4 (counterclockwise)
    # We'll use three-point arc: start, middle, end
    # Middle point is at angle halfway between angle3 and angle4
    # Going the shorter way (counterclockwise from p3 to p4)
    # p3 is at ~1.57 rad (top-right), p4 is at ~-1.57 rad (top-left)
    # Going CCW from p3 to p4 means going through angles > 1.57 up to pi, then -pi to -1.57
    # Actually, let's just use the three-point arc with a computed midpoint

    mid_angle = (angle3 + angle4) / 2
    if angle4 < angle3:
        mid_angle = (angle3 + angle4 + 2*math.pi) / 2
        if mid_angle > math.pi:
            mid_angle -= 2*math.pi

    mid_x = cx + r * math.cos(mid_angle)
    mid_y = cy + r * math.sin(mid_angle)

    # Add the arc using three-point arc
    wire = wire.threePointArc((mid_x, mid_y), (p4[0], p4[1]))

    # Close the wire back to p1
    wire = wire.close()

    # Now extrude the outer profile
    result = wire.extrude(extrude_distance)

    # Now we need to add the second profile (profile 2) which is a similar shape
    # but with a through hole (inner circle of radius 1.25)
    # Actually, looking at the design plan more carefully:
    # Profile 1 and Profile 2 are two separate profiles that together form the solid.
    # Profile 1 is the base shape (rectangle with circular top).
    # Profile 2 is the same shape but with a hole.
    # This suggests the part has a through hole.

    # Let's re-examine: The design plan has two profiles, both extruded together.
    # Profile 1: outer ring (no inner hole)
    # Profile 2: outer ring with inner hole
    # This is unusual - typically you'd have one profile with the hole.
    # But the design plan explicitly lists two profiles.

    # Let's interpret this as: Profile 1 defines the outer boundary,
    # Profile 2 defines the same outer boundary but with an inner hole.
    # The extrusion is a single operation (extrude distance 18mm).
    # So the final shape is the outer shape from profile 1 with a through hole from profile 2.

    # Cut the through hole (inner circle of radius 1.25)
    # The inner circle is centered at (2.3181225581176115, 1.7490620724718653)
    # with radius 1.25

    # Create a cutting cylinder
    cut_cylinder = cq.Workplane("XY").moveTo(cx, cy).circle(1.25).extrude(extrude_distance * 1.5)

    # Cut the hole
    result = result.cut(cut_cylinder)

    # Export the result
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
