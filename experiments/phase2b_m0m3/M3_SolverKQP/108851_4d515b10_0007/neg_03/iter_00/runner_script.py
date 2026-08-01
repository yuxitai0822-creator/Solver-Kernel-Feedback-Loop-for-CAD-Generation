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

    # Design Plan: SoapCutterBackBar1 v1
    # Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
    # The profile is defined in UV space where:
    #   u_dir = [1,0,0] (X axis)
    #   v_dir = [0,0,-1] (negative Z axis)
    #   w_dir = [0,1,0] (Y axis)
    # The rectangle in UV coordinates:
    #   (0.0, 5.08) -> (0.0, 0.0) -> (27.94, 0.0) -> (27.94, 5.08) -> back to start
    # Note: The UV coordinates are scaled by 10 (cm to mm conversion).
    #   u values: 0.0 to 27.94 (mm) -> actual X span = 27.94 mm? 
    #   But dimensions say length_u = 279.4 mm, width_v = 50.8 mm.
    #   The UV rectangle is 27.94 x 5.08, which is 1/10 of the target.
    #   This matches the compiler note: unit_conversion_applied = cm_to_mm (x10).
    #   So the UV coordinates are in cm, and we must scale by 10 to get mm.
    #   Alternatively, the profile curves are already in mm after conversion.
    #   Let's check: start_uv = [0.0, 5.08], end_uv = [0.0, 0.0] -> v goes from 5.08 to 0.0, span = 5.08
    #   But width_v = 50.8 mm. So 5.08 * 10 = 50.8. Yes, UV is in cm, scale by 10.
    #   Similarly, u span = 27.94 * 10 = 279.4 mm. Correct.
    #
    # The frame: u_dir = X, v_dir = -Z, w_dir = Y.
    # So in world coordinates:
    #   u (X) maps to X axis
    #   v (-Z) maps to negative Z axis
    #   w (Y) maps to Y axis
    # The rectangle in UV: (0,5.08) to (0,0) to (27.94,0) to (27.94,5.08)
    # In world: X from 0 to 27.94*10=279.4, Z from -5.08*10=-50.8 to 0 (since v_dir = -Z, v=0 -> Z=0, v=5.08 -> Z=-50.8)
    # But the rectangle starts at v=5.08 (Z=-50.8) and goes to v=0 (Z=0).
    # So the rectangle spans X: [0, 279.4], Z: [-50.8, 0].
    # Extrude in +w direction = +Y direction, distance = 19.05 mm.

    # Build the rectangle on the XZ plane (since v_dir = -Z, the sketch plane is XZ).
    # We'll use Workplane("XZ") and draw the rectangle.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0007\neg_03\iter_00\generated.step"

    # Scale factor from UV (cm) to mm
    scale = 10.0

    # UV coordinates (in cm)
    u_min = 0.0
    u_max = 27.94
    v_min = 0.0
    v_max = 5.08

    # Convert to mm and map to world coordinates:
    # world_x = u * scale
    # world_z = -v * scale  (because v_dir = [0,0,-1])
    # So the rectangle corners in world (XZ plane):
    # (0, -50.8) -> (0, 0) -> (279.4, 0) -> (279.4, -50.8)

    x0 = u_min * scale  # 0.0
    x1 = u_max * scale  # 279.4
    z0 = -v_max * scale  # -50.8
    z1 = -v_min * scale  # 0.0

    # Create workplane on XZ
    wp = cq.Workplane("XZ")

    # Draw rectangle: move to start point, then lineTo for each edge
    # Start at (x0, z0) = (0, -50.8)
    # Then line to (x0, z1) = (0, 0)
    # Then line to (x1, z1) = (279.4, 0)
    # Then line to (x1, z0) = (279.4, -50.8)
    # Then close

    # Using rect() is simpler: center at ((x0+x1)/2, (z0+z1)/2), width = x1-x0, height = z1-z0
    # But rect() expects width and height as positive numbers, and center.
    # The rectangle spans x: [0, 279.4], z: [-50.8, 0]
    # Center: (139.7, -25.4)
    # Width: 279.4, Height: 50.8

    center_x = (x0 + x1) / 2.0
    center_z = (z0 + z1) / 2.0
    width = x1 - x0
    height = z1 - z0  # This is 50.8 (positive)

    # Build the rectangle
    result = (wp
        .center(center_x, center_z)
        .rect(width, height)
        .extrude(19.05)  # extrude in +Y direction (normal to XZ plane)
    )

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
