import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile based on the design plan
    # The profile is a rectangle with dimensions 19.0 x 19.0 mm
    # The rectangle is defined in UV coordinates where:
    #   u_dir = (1,0,0)  -> X axis
    #   v_dir = (0,0,-1) -> -Z axis
    #   w_dir = (0,1,0)  -> Y axis
    # The rectangle corners are at:
    #   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
    # This gives a rectangle of width 1.9 (in U) and height 1.9 (in V) but the dimensions say 19.0 x 19.0
    # The unit conversion was cm_to_mm (x10), so the UV coordinates are in cm and need scaling to mm
    # Actually, the design plan says unit is mm, but compiler notes say cm_to_mm (x10)
    # The UV coordinates appear to be in cm (since 1.9 cm = 19 mm), so we'll use them directly as mm
    # after scaling by 10? Let's check: difference in U: -56.378 - (-58.278) = 1.9, difference in V: -13.940 - (-12.040) = -1.9
    # So the rectangle is 1.9 x 1.9 in UV space. With cm_to_mm conversion, that's 19 x 19 mm.
    # We'll build the rectangle at the correct location and extrude along w_dir (Y axis) by 130 mm.

    # Define the rectangle center and size
    # Center of rectangle in UV: ((-58.278 + -56.378)/2, (-12.040 + -13.940)/2) = (-57.328, -12.990)
    # But we need to convert to world coordinates:
    #   world = origin + u * u_dir + v * v_dir
    #   origin is (0,0,0) since bbox_min_corner convention
    #   u_dir = (1,0,0), v_dir = (0,0,-1)
    # So world_x = u, world_z = -v, world_y = 0 initially

    # Let's build the rectangle in the XY plane (since we'll extrude along Y)
    # The rectangle in UV: u from -58.278 to -56.378, v from -13.940 to -12.040
    # In world: x = u, z = -v, so z from 12.040 to 13.940
    # But we want to extrude along w_dir = (0,1,0) = Y axis
    # So we create the rectangle in the XZ plane and extrude along Y

    # Rectangle dimensions: width = 1.9 (in U), height = 1.9 (in V) -> after cm_to_mm: 19 x 19 mm
    # Position: center at x = -57.328, z = 12.990 (since z = -v, v_center = -12.990, so z = 12.990)

    # Create the rectangle in the XZ plane (normal = Y axis)
    result = (
        cq.Workplane("XZ")
        .center(-57.328, 12.990)
        .rect(19.0, 19.0)
        .extrude(130.0)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100243_9fb796fe_0006\\neg_01/generated.step")

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
