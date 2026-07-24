import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
    # The profile is defined in the UV plane where:
    #   u_dir = (1,0,0) -> X axis
    #   v_dir = (0,0,-1) -> negative Z axis
    #   w_dir = (0,1,0) -> Y axis (extrude direction)
    #
    # The rectangle corners in UV space:
    #   (7.83, -66.34) to (127.83, -6.34)
    # But the actual dimensions are length_u=1200, width_v=600.
    # The UV coordinates given are scaled/offset from the actual dimensions.
    # We'll construct the rectangle centered at origin with the correct dimensions.

    # Create the rectangle profile on the XY plane (since u_dir=X, v_dir=-Z, w_dir=Y)
    # We'll work in the XY plane and extrude along Y

    # Rectangle dimensions
    length_u = 1200.0  # along X
    width_v = 600.0    # along Z (negative direction in v_dir)
    extrude_dist = 20.0  # along Y

    # Create the base rectangle centered at origin on XY plane
    result = (
        cq.Workplane("XY")
        .rect(length_u, width_v)
        .extrude(extrude_dist)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0004\\ex2/generated.step")

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
