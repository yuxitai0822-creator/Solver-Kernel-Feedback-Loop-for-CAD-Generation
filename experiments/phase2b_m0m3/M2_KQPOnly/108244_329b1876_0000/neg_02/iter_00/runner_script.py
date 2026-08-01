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

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # Profile rectangle corners in UV space:
    #   start_uv = (121.17356129030935, 31.299551148092803)
    #   end_uv = (-0.7464387096940412, 290.379551148076)
    # These are the min/max of the rectangle in UV coordinates.
    # The rectangle spans from u_min to u_max and v_min to v_max.

    # Extract UV bounds from the design plan curves
    # From curves:
    #   line1: (121.17356129030935, 31.299551148092803) -> (-0.7464387096940412, 31.299551148092803)  (horizontal, v constant)
    #   line2: (121.17356129030935, 290.379551148076) -> (121.17356129030935, 31.299551148092803)  (vertical, u constant)
    #   line3: (-0.7464387096940412, 290.379551148076) -> (121.17356129030935, 290.379551148076)  (horizontal, v constant)
    #   line4: (-0.7464387096940412, 31.299551148092803) -> (-0.7464387096940412, 290.379551148076)  (vertical, u constant)
    # So u_min = -0.7464387096940412, u_max = 121.17356129030935
    # v_min = 31.299551148092803, v_max = 290.379551148076
    # But the design plan says length_u = 1219.2, width_v = 2590.8
    # The UV coordinates are in cm (since compiler notes say cm_to_mm x10 was applied).
    # Actually, the original values were in cm, and the conversion to mm multiplies by 10.
    # The UV coordinates given are already in mm? Let's check:
    # u_span = 121.17356129030935 - (-0.7464387096940412) = 121.92 mm? No, that's 121.92, not 1219.2.
    # Wait, the design plan says length_u = 1219.2, which is 10x larger.
    # The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # So the UV coordinates are in cm, and we need to multiply by 10 to get mm.
    # Let's verify: u_span_cm = 121.17356129030935 - (-0.7464387096940412) = 121.92 cm = 1219.2 mm. Yes!
    # v_span_cm = 290.379551148076 - 31.299551148092803 = 259.08 cm = 2590.8 mm. Yes!
    # So we need to scale the UV coordinates by 10 to get mm.

    SCALE = 10.0  # cm to mm

    u_min = -0.7464387096940412 * SCALE
    u_max = 121.17356129030935 * SCALE
    v_min = 31.299551148092803 * SCALE
    v_max = 290.379551148076 * SCALE

    # Rectangle dimensions in mm
    length_u = u_max - u_min  # should be 1219.2
    width_v = v_max - v_min  # should be 2590.8
    extrude_dist = 44.45  # mm

    # The frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means:
    #   u axis = world X
    #   v axis = world -Z (negative Z)
    #   w axis = world Y
    # So the sketch plane is X-Z (since u=X, v=-Z), and extrude direction is +Y (w_dir).
    # In cadquery, we can work on the XZ plane and extrude in Y direction.

    # Build the rectangle in UV space, then transform to world coordinates.
    # The rectangle center in UV space:
    center_u = (u_min + u_max) / 2.0
    center_v = (v_min + v_max) / 2.0

    # Create the workplane on XZ plane (Y=0)
    # We'll create a rectangle centered at (center_u, -center_v) because v_dir = [0,0,-1]
    # So v coordinate maps to world -Z.
    # Actually, let's think carefully:
    #   u coordinate -> world X
    #   v coordinate -> world -Z (since v_dir = [0,0,-1])
    # So a point (u, v) in UV space maps to world (u, 0, -v).
    # The rectangle in UV space spans [u_min, u_max] x [v_min, v_max].
    # In world space, it spans X: [u_min, u_max], Z: [-v_max, -v_min].
    # The center in world space is (center_u, 0, -center_v).

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Move to the center of the rectangle in world coordinates
    # Note: cadquery's rect() creates a rectangle centered at the current point.
    # The rectangle is aligned with the workplane axes (X and Z for XZ plane).
    # So we just need to move to the center and draw the rectangle.
    wp = wp.moveTo(center_u, -center_v)  # world X, world Z

    # Draw the rectangle with dimensions length_u (along X) and width_v (along Z)
    wp = wp.rect(length_u, width_v, centered=True)

    # Extrude in the +Y direction (w_dir = [0,1,0])
    result = wp.extrude(extrude_dist)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108244_329b1876_0000\neg_02\iter_00/generated.step"
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
