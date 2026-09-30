import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
    # The design plan specifies a flat plate/panel with extruded rectangle profile
    # The profile is defined in a local frame where:
    #   u_dir = (1,0,0) -> x-axis
    #   v_dir = (0,0,-1) -> negative z-axis
    #   w_dir = (0,1,0) -> y-axis (extrusion direction)
    # The rectangle corners in UV space are:
    #   (127.82976, -66.34402) to (7.82976, -6.34402)
    # This gives length_u = 120.0 and width_v = 60.0 in the original units (cm)
    # After unit conversion (cm_to_mm x10): length = 1200mm, width = 600mm
    # Extrude distance = 20mm (already in mm)

    # Build the rectangle profile in the XY plane (since we'll work in world coords)
    # The rectangle spans from x=7.82976 to x=127.82976 (width 120) in original units
    # and from y=-66.34402 to y=-6.34402 (height 60) in original units
    # After scaling by 10 (cm to mm): x from 78.2976 to 1278.2976, y from -663.4402 to -63.4402
    # But we can simplify: just create a 1200x600 rectangle centered at origin
    # and extrude 20mm in the y-direction (since w_dir = (0,1,0))

    # Actually, let's follow the exact UV coordinates scaled by 10:
    x_start = 7.829761315356478 * 10  # 78.2976
    x_end = 127.82976131535646 * 10    # 1278.2976
    y_start = -66.34402294937294 * 10  # -663.4402
    y_end = -6.344022949372942 * 10    # -63.4402

    # Width in x = 1200mm, height in y = 600mm (as expected)
    # Extrude in +w direction = +y direction, distance = 20mm

    result = (
        cq.Workplane("XY")
        .rect(x_end - x_start, y_end - y_start)
        .extrude(20.0)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0004\\neg_03/generated.step")

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
