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

    # Design Plan: SoapCutterLeg1 v1
    # Extruded rectangle: 209.55 x 57.912 x 19.05 mm
    # Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
    # Rectangle in uv-plane: u from 0 to 209.55, v from 0 to 57.912
    # Extrude along +w (y-axis) by 19.05 mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0009\neg_03\iter_00/generated.step"

    # Build the rectangle in the XZ plane (since v_dir = [0,0,-1] means v is along -z, u along x)
    # The rectangle corners in uv: (0,0), (209.55,0), (209.55,57.912), (0,57.912)
    # In world: u->x, v-> -z, so point (u,v) -> (u, 0, -v)
    # But we can just use Workplane("XZ") and draw rectangle centered at (104.775, -28.956)
    # with width=209.55, height=57.912, then extrude along y (positive w direction)

    wp = cq.Workplane("XZ")

    # Rectangle centered at (104.775, -28.956) with size (209.55, 57.912)
    # The rectangle spans u:0..209.55, v:0..57.912, so center in uv is (104.775, 28.956)
    # In XZ plane: x = u, z = -v, so center is (104.775, -28.956)
    result = wp.moveTo(104.775, -28.956).rect(209.55, 57.912, centered=True).extrude(19.05)

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
