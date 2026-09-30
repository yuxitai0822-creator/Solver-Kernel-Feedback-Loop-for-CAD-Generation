import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # Length (u direction) = 171.45 mm, Width (v direction) = 38.1 mm, Extrude distance (w direction) = 6.35 mm
    # The profile is defined in UV space where:
    #   u_dir = [1.0, 0.0, 0.0] (X axis)
    #   v_dir = [0.0, 0.0, -1.0] (Z axis, negative)
    #   w_dir = [0.0, 1.0, 0.0] (Y axis)
    # The rectangle corners in UV: (0,0), (17.145,0), (17.145,3.81), (0,3.81)
    # Note: The UV coordinates are in cm (from compiler notes: cm_to_mm x10), so multiply by 10 to get mm
    # 17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm

    # Build the rectangle profile in the XY plane (since we'll orient it later)
    # Actually, let's build it directly in the correct orientation:
    # The frame has u_dir = X, v_dir = -Z, w_dir = Y
    # So the rectangle lies in the X-Z plane, and extrudes along Y

    # Create a rectangle centered at origin for simplicity, then translate
    length = 171.45  # mm (u direction = X)
    width = 38.1     # mm (v direction = -Z, so magnitude in Z)
    thickness = 6.35 # mm (w direction = Y)

    # Build the profile on the XZ plane (since v_dir = -Z, we use Z for v)
    # The rectangle corners in UV: (0,0) -> (171.45, 0) -> (171.45, 38.1) -> (0, 38.1)
    # In XYZ: (0, 0, 0) -> (171.45, 0, 0) -> (171.45, 0, -38.1) -> (0, 0, -38.1)
    # But we want the plate to be centered for easier handling, then translate

    # Create the rectangle on the XZ plane, then extrude along Y
    result = (
        cq.Workplane("XZ")
        .rect(length, width, centered=False)
        .extrude(thickness)
    )

    # The rect() with centered=False places the first corner at (0,0) in the workplane
    # For XZ workplane: center is at (0,0), rect creates from center by default
    # With centered=False, the rectangle starts at (0,0) and goes to (length, width)
    # But we need it to start at (0,0) and go to (length, -width) because v_dir = -Z
    # So we'll create it manually with a polygon

    # Alternative: use a simple box with proper dimensions and position
    result = cq.Workplane("XY").box(length, thickness, width).translate((length/2, thickness/2, -width/2))

    # Wait, let's re-think the orientation:
    # u_dir = X, v_dir = -Z, w_dir = Y
    # So the plate spans: 0 to 171.45 in X, 0 to -38.1 in Z, and extrudes 0 to 6.35 in Y
    # The box should have dimensions: length along X = 171.45, width along Z = 38.1, height along Y = 6.35
    # Position: min corner at (0, 0, -38.1) -> center at (85.725, 3.175, -19.05)

    result = cq.Workplane("XY").box(length, thickness, width).translate((length/2, thickness/2, -width/2))

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108850_0dcd5ef1_0002\neg_02/generated.step")

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
