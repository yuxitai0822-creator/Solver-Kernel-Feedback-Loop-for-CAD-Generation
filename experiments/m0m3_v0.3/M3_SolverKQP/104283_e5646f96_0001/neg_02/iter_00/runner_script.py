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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0001\neg_02\iter_00/generated.step"

    # Design Plan interpretation:
    # - Two profiles: first is a closed shape with 4 curves (3 lines + 1 circle arc)
    # - Second profile: outer ring with 4 curves (circle, line, circle, line) and inner circle hole
    # - Extrude 18.0 mm in +Z direction
    # - The geometry appears to be a rectangular plate with a circular boss and a concentric hole

    # Build the base plate (first profile)
    # From the curves: 
    # Line from (0.9188, 1.7937) to (0.9188, 0.0)
    # Line from (0.9188, 0.0) to (3.8000, 0.0)
    # Line from (3.7174, 1.7937) to (3.7174, 0.0)
    # Circle at (2.3181, 1.7491) radius 1.4
    # This forms a shape like a rectangle with a circular arc on top

    # First, create the base profile (outer boundary of first profile)
    base_wp = cq.Workplane("XY")

    # Build the first profile: a closed shape with 3 lines and 1 circle arc
    # The circle arc connects the two vertical lines at the top
    p1 = (0.9188335453558412, 1.7936743887554851)
    p2 = (0.9188335453558412, 0.0)
    p3 = (3.8000000566244125, 0.0)
    p4 = (3.7174115708793822, 1.7936743887554851)
    circle_center = (2.3181225581176115, 1.7490620724718653)
    circle_radius = 1.4

    # Create the base shape using a polyline and arc
    # Start at p1, go down to p2, right to p3, then arc to p4, then back to p1
    # The arc goes from p4 to p1 (or p1 to p4) - we need to determine the correct direction

    # Calculate angles for the arc endpoints relative to circle center
    angle_p1 = math.atan2(p1[1] - circle_center[1], p1[0] - circle_center[0])
    angle_p4 = math.atan2(p4[1] - circle_center[1], p4[0] - circle_center[0])

    # The arc should go from p4 to p1 (counterclockwise)
    # Check if p4 is at a larger angle than p1
    if angle_p4 < angle_p1:
        angle_p4 += 2 * math.pi

    # Build the wire using points and arc
    # Start at p1, line to p2, line to p3, arc to p4, line back to p1
    # But cadquery's threePointArc needs three points: start, mid, end
    # We'll use a different approach: create the full circle and intersect

    # Alternative: build the shape as a rectangle with a circular top
    # The shape is essentially: rectangle from x=0.9188 to x=3.8, y=0 to y=1.7937
    # with a circular arc replacing the top edge

    # Let's build it step by step using a polyline and arc
    # Start at bottom-left corner
    wp = base_wp.moveTo(p2[0], p2[1])  # (0.9188, 0.0)
    wp = wp.lineTo(p3[0], p3[1])  # (3.8, 0.0)
    wp = wp.lineTo(p4[0], p4[1])  # (3.7174, 1.7937)

    # Now add the arc from p4 to p1
    # We need a point on the arc between p4 and p1
    mid_angle = (angle_p4 + angle_p1) / 2
    mid_x = circle_center[0] + circle_radius * math.cos(mid_angle)
    mid_y = circle_center[1] + circle_radius * math.sin(mid_angle)
    wp = wp.threePointArc((mid_x, mid_y), (p1[0], p1[1]))

    # Close back to start
    wp = wp.close()

    # Extrude the base profile
    result = wp.extrude(18.0)

    # Now create the second profile features:
    # Outer ring: circle at (2.3181, 1.7491) radius 1.4, then lines, then circle again
    # Inner hole: circle at same center, radius 1.25

    # The second profile seems to describe a circular boss on top of the base
    # with a concentric hole through it

    # Create the circular boss (outer circle of second profile)
    # The boss center is at (2.3181, 1.7491) with radius 1.4
    # But this overlaps with the base - we need to add material

    # Actually, looking at the design plan more carefully:
    # The first profile creates the base shape
    # The second profile has an outer ring (circle + lines + circle + lines) and inner circle
    # This likely represents a cylindrical feature with a hole

    # Let's create the boss as a cylinder
    boss_center = (2.3181225581176115, 1.7490620724718653)
    boss_outer_radius = 1.4
    boss_inner_radius = 1.25

    # Create the outer cylinder (boss)
    boss = cq.Workplane("XY").moveTo(boss_center[0], boss_center[1]).circle(boss_outer_radius).extrude(18.0)

    # Union the boss with the base
    result = result.union(boss)

    # Create the inner hole (through all)
    hole = cq.Workplane("XY").moveTo(boss_center[0], boss_center[1]).circle(boss_inner_radius).extrude(18.0)

    # Cut the hole
    result = result.cut(hole)

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
