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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0004\neg_03\iter_02\generated.step"

    # Design parameters from the design plan
    # Rectangle dimensions: length_u = 1200.0 mm, width_v = 600.0 mm
    # Extrude distance: 20.0 mm along w direction (which is [0,1,0] in world frame)
    # The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # The profile coordinates in UV space are given, but we can just use the dimensions directly

    # The profile rectangle in UV coordinates:
    # start_uv: (127.82976131535646, -66.34402294937294) to (7.829761315356478, -66.34402294937294)
    # This gives a width in U of 120.0 and height in V of 60.0
    # But the dimensions say length_u=1200.0 and width_v=600.0
    # The UV coordinates seem to be in cm (since compiler notes say cm_to_mm x10)
    # So the actual rectangle in mm is 1200 x 600

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # The rectangle center is at (127.82976131535646 + 7.829761315356478)/2 = 67.82976131535647 in U
    # and (-66.34402294937294 + -6.344022949372942)/2 = -36.34402294937294 in V
    # But we'll just use the dimensions directly for clarity

    # Create the workplane on XZ (since v_dir is [0,0,-1], the sketch plane normal is w_dir=[0,1,0])
    # So the sketch plane is XZ
    result = (cq.Workplane("XZ")
        .center(67.82976131535647, -36.34402294937294)  # center of the rectangle in UV space
        .rect(120.0, 60.0)  # width=120 in U, height=60 in V (these are in cm, but we'll extrude 20mm)
        .extrude(20.0)  # extrude along w_dir=[0,1,0] by 20mm
    )

    # Export to STEP
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
