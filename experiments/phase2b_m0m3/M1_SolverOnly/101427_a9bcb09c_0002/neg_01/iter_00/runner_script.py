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

    # Design Plan: extruded rectangle 193.0 x 55.0 x 50.0 mm (after cm->mm conversion)
    # The previous script used 75.0 mm extrusion (perturbed value 7.5 cm = 75 mm)
    # but the design plan specifies 50.0 mm extrusion.
    # Also the rectangle dimensions in the design plan are 193.0 x 55.0 mm (after cm->mm conversion)
    # The previous script used 1930.0 x 550.0 which is 10x too large.
    # The design plan states unit conversion applied: cm_to_mm (x10)
    # So original cm values: length_u=193.0 cm -> 1930 mm, width_v=55.0 cm -> 550 mm
    # But the profile curves show start_uv/end_uv values: 0-193 and 0-55
    # These are in the local UV frame, not yet scaled.
    # The dimensions section says length_u=1930.0, width_v=550.0 (in mm after conversion)
    # The profile curves use 193 and 55 which are the cm values before scaling.
    # We'll use the explicit dimensions: 1930 x 550 x 50 mm

    # Build the rectangle on the XZ plane (as per previous script's WORKPLANE='XZ')
    # The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So u -> X, v -> -Z, w -> Y
    # Extrude in +w direction = +Y

    result = (
        cq.Workplane("XZ")
        .center(1930.0/2, 550.0/2)  # center of rectangle
        .rect(1930.0, 550.0)
        .extrude(50.0)  # extrude in +Y direction
    )

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0002\neg_01\iter_00/generated.step"
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
