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

    # Design Plan: basic slat v1 (5)
    # Extruded rectangle: 95.25 mm x 571.5 mm x 19.05 mm
    # The profile is a rectangle in the UV plane, where:
    #   U direction = (1,0,0) = X axis
    #   V direction = (0,0,-1) = -Z axis
    #   W direction = (0,1,0) = Y axis (extrude direction)
    # Profile rectangle corners in UV:
    #   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
    # But the dimensions say length_u = 95.25, width_v = 571.5
    # The UV coordinates given are 9.525 and 57.15, which are 1/10 of the actual dimensions.
    # This is because the original data was in cm and converted to mm (x10).
    # So the actual rectangle in mm is: 95.25 mm x 571.5 mm
    # The extrude distance is 19.05 mm along +W (Y axis)

    # Build the part
    result = (
        cq.Workplane("XY")
        .rect(95.25, 571.5, centered=True)
        .extrude(19.05)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101269_f084ba14_0023\neg_01\iter_00/generated.step"
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
