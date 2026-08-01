import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101269_f084ba14_0023\neg_02\iter_02\generated.step"

    # Design Plan: extruded rectangle
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # The design plan dimensions: length_u=95.25, width_v=571.5, extrude_distance=19.05
    # The perturbation changes the u-dimension from 9.525 to 11.43 (in cm)
    # After cm-to-mm conversion (x10): 11.43 cm = 114.3 mm
    # The kernel feedback from iteration 1 shows:
    #   expected u=95.25, actual u=114.3 (error=19.05)
    #   expected v=571.5, actual v=571.5 (pass)
    #   expected w=19.05, actual w=19.05 (pass)
    # The perturbation is applied correctly: the rectangle in UV space is u from 0 to 114.3, v from 0 to 571.5
    # In world coordinates:
    #   u_dir = [1, 0, 0] -> x axis
    #   v_dir = [0, 0, -1] -> -z axis
    #   w_dir = [0, 1, 0] -> y axis
    # So the rectangle in world: x from 0 to 114.3, z from -571.5 to 0
    # Extrude in +y direction by 19.05 mm

    # Build the rectangle using a polyline in the XZ plane
    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(114.3, 0)
        .lineTo(114.3, -571.5)
        .lineTo(0, -571.5)
        .close()
        .extrude(19.05)
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
