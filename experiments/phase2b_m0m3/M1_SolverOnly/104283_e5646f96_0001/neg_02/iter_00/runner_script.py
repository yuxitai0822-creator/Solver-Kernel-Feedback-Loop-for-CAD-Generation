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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0001\neg_02\iter_00\generated.step"

    # Design parameters from the design plan
    # The profile consists of two profiles:
    # Profile 1: outer ring with 4 curves (3 lines + 1 circle)
    # Profile 2: outer ring with 4 curves (2 circles + 2 lines) and inner circle

    # From the design plan, the key dimensions (in mm after cm->mm conversion):
    # The outer shape is defined by:
    # - Left vertical line: x=0.9188335453558412, y from 0 to 1.7936743887554851
    # - Bottom horizontal line: from (0.9188335453558412, 0) to (3.8000000566244125, 0)
    # - Right vertical line: x=3.7174115708793822, y from 0 to 1.7936743887554851
    # - Circle: center at (2.3181225581176115, 1.7490620724718653), radius=1.4
    #
    # The inner hole is a circle: center at (2.3181225581176115, 1.7490620724718653), radius=1.25
    #
    # Extrude distance: 18.0 mm

    # Scale factor: the design plan says unit conversion cm_to_mm (x10)
    # So the values in the plan are in cm, we need to multiply by 10 to get mm
    scale = 10.0

    # Profile 1: outer shape (the "D"-like shape)
    # Points in cm, convert to mm
    left_x = 0.9188335453558412 * scale
    right_x = 3.7174115708793822 * scale
    bottom_y = 0.0
    # The top y for the vertical lines
    # From the curves: start_uv and end_uv for the vertical lines have y=1.7936743887554851
    top_y = 1.7936743887554851 * scale
    # The circle center and radius
    circle_cx = 2.3181225581176115 * scale
    circle_cy = 1.7490620724718653 * scale
    circle_r = 1.4 * scale

    # Inner hole radius
    inner_r = 1.2500000000000002 * scale

    # Extrude distance
    extrude_dist = 18.0

    # Build the profile using cadquery
    # We'll create the base shape by:
    # 1. Create a rectangle for the main body
    # 2. Add the circular arc at the top
    # 3. Cut the inner hole

    # Approach: Use a workplane and build the profile with lines and arcs
    wp = cq.Workplane("XY")

    # Start at the bottom-left corner of the shape
    # The shape consists of:
    # - Left vertical line from (left_x, 0) to (left_x, top_y)
    # - Then a circular arc from (left_x, top_y) to (right_x, top_y) with center at (circle_cx, circle_cy)
    # - Right vertical line from (right_x, top_y) to (right_x, 0)
    # - Bottom horizontal line from (right_x, 0) to (left_x, 0)

    # Build the outer profile
    # Start at bottom-left
    p = cq.Workplane("XY")
    p = p.moveTo(left_x, 0)

    # Left vertical line up
    p = p.lineTo(left_x, top_y)

    # Circular arc from left_x to right_x
    # The arc goes from the left point to the right point, with center at (circle_cx, circle_cy)
    # We need to compute the start and end angles
    start_angle = math.degrees(math.atan2(top_y - circle_cy, left_x - circle_cx))
    end_angle = math.degrees(math.atan2(top_y - circle_cy, right_x - circle_cx))

    # The arc should go the shorter way around
    # Since the center is below the top line, the arc goes from left to right
    # We'll use threePointArc instead for reliability
    # Points: start (left_x, top_y), middle (circle_cx, circle_cy + circle_r), end (right_x, top_y)
    mid_x = circle_cx
    mid_y = circle_cy + circle_r
    p = p.threePointArc((mid_x, mid_y), (right_x, top_y))

    # Right vertical line down
    p = p.lineTo(right_x, 0)

    # Bottom horizontal line back to start
    p = p.lineTo(left_x, 0)

    # Close the wire
    p = p.close()

    # Extrude the outer shape
    result = p.extrude(extrude_dist)

    # Now cut the inner hole
    # Create a circle at the center
    hole = cq.Workplane("XY").moveTo(circle_cx, circle_cy).circle(inner_r).extrude(extrude_dist)

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
