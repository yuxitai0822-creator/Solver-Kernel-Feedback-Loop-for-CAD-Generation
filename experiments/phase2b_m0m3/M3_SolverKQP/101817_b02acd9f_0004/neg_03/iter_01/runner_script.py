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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0004\neg_03\iter_01/generated.step"

    # Design Plan: extruded rectangle
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Rectangle in UV plane: u from 7.82976 to 127.82976, v from -66.34402 to -6.34402
    # Dimensions: length_u=1200.0, width_v=600.0 (original cm values converted to mm: 1200x600)
    # Extrude distance: 20.0 mm along +w (which is +Y in world)

    # The previous script incorrectly divided by 10 (cm->mm conversion was already applied in the design plan)
    # The design plan explicitly states dimensions: length_u=1200.0, width_v=600.0 in mm
    # The UV coordinates are in mm as well, so we use them directly

    # Rectangle center in UV: ((7.82976+127.82976)/2, (-66.34402+-6.34402)/2) = (67.82976, -36.34402)
    # Rectangle dimensions: width_u = 120.0, height_v = 60.0 (from UV bounds: 127.82976-7.82976=120, -6.34402-(-66.34402)=60)
    # But the design plan says length_u=1200.0, width_v=600.0
    # The UV coordinates span 120 in u and 60 in v, but the actual part dimensions should be 1200x600
    # This means the UV coordinates are in a different scale (1:10) relative to the actual dimensions
    # We need to scale the rectangle to match the specified dimensions

    # Create workplane on XZ (since u_dir=X, v_dir=-Z, w_dir=Y)
    wp = cq.Workplane("XZ")

    # Use the specified dimensions directly: 1200 x 600 mm
    # Center the rectangle at the origin for simplicity (the UV coordinates are just for reference)
    # The extrusion is 20 mm along +Y
    result = wp.rect(1200.0, 600.0, centered=True).extrude(20.0)

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
