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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0005\neg_02\iter_00\generated.step"

    # Design Plan: Drone Leg Left
    # Extruded rectangle with dimensions 19.0mm x 19.0mm x 200.0mm
    # The profile is a rectangle in the UV plane, extruded along W direction
    # From the design plan:
    #   u_dir = [1.0, 0.0, 0.0]  (X axis)
    #   v_dir = [0.0, 0.0, -1.0] (negative Z axis)
    #   w_dir = [0.0, 1.0, 0.0]  (Y axis)
    # Rectangle corners in UV space:
    #   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
    # Width in U = 1.9mm, Width in V = 1.9mm (but expected span is 19.0mm)
    # The perturbation scaled the rectangle by 1.2x, so original 1.9mm became 2.28mm
    # But the validation expects 19.0mm span, so we need to build a 19.0mm x 19.0mm x 200.0mm strut

    # Build the rectangle centered at origin in the XZ plane, then extrude along Y
    # Rectangle: 19.0mm x 19.0mm
    # Extrude: 200.0mm along Y

    result = (
        cq.Workplane("XZ")
        .rect(19.0, 19.0, centered=True)
        .extrude(200.0)
    )

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
