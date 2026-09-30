import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0001\neg_02\iter_01/generated.step"

    # Design Plan interpretation:
    # - Single solid body with a base profile (rectangle with circular arc top) and a concentric through-hole
    # - The base is extruded 18mm, and a cylindrical boss with a concentric hole is added
    # - The previous script produced 2 bodies (non-manifold) because the boss and base were separate solids
    # - Fix: Create the entire shape as a single continuous solid using proper boolean operations

    # Define key points from the design plan
    p1 = (0.9188335453558412, 1.7936743887554851)
    p2 = (0.9188335453558412, 0.0)
    p3 = (3.8000000566244125, 0.0)
    p4 = (3.7174115708793822, 1.7936743887554851)
    circle_center = (2.3181225581176115, 1.7490620724718653)
    circle_radius = 1.4
    boss_inner_radius = 1.2500000000000002

    # Calculate angles for arc endpoints
    angle_p1 = math.atan2(p1[1] - circle_center[1], p1[0] - circle_center[0])
    angle_p4 = math.atan2(p4[1] - circle_center[1], p4[0] - circle_center[0])
    if angle_p4 < angle_p1:
        angle_p4 += 2 * math.pi

    # Build the base profile (first profile from design plan)
    # Start at bottom-left corner (p2), go right to p3, up to p4, arc to p1, close back to p2
    wp = cq.Workplane("XY")
    wp = wp.moveTo(p2[0], p2[1])  # (0.9188, 0.0)
    wp = wp.lineTo(p3[0], p3[1])  # (3.8, 0.0)
    wp = wp.lineTo(p4[0], p4[1])  # (3.7174, 1.7937)

    # Add the arc from p4 to p1
    mid_angle = (angle_p4 + angle_p1) / 2
    mid_x = circle_center[0] + circle_radius * math.cos(mid_angle)
    mid_y = circle_center[1] + circle_radius * math.sin(mid_angle)
    wp = wp.threePointArc((mid_x, mid_y), (p1[0], p1[1]))

    # Close back to start (p2)
    wp = wp.close()

    # Extrude the base profile to create the main body
    result = wp.extrude(18.0)

    # Now add the cylindrical boss (second profile outer ring)
    # The boss is a cylinder at the same center, radius 1.4, extruded 18mm
    # Since it overlaps with the base, we union them to create a single solid
    boss = cq.Workplane("XY").moveTo(circle_center[0], circle_center[1]).circle(circle_radius).extrude(18.0)
    result = result.union(boss)

    # Cut the concentric through-hole (inner circle of second profile)
    hole = cq.Workplane("XY").moveTo(circle_center[0], circle_center[1]).circle(boss_inner_radius).extrude(18.0)
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
