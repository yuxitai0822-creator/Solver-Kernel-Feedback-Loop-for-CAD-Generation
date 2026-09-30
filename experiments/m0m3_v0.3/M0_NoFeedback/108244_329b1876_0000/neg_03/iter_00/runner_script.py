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

    # Design Plan: extruded rectangle (flat plate/panel)
    # Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle corners in UV space:
    #   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
    #   This gives width in U = 121.92, height in V = 259.08 (but scaled?)
    #   Actually the design plan says length_u=1219.2, width_v=2590.8
    #   The UV coordinates seem to be in cm (divided by 10). Let's use the explicit dimensions.

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1], w_dir is [0,1,0])
    # The frame: u along X, v along -Z, w along Y
    # So the sketch plane is XZ, extrude along Y

    # Rectangle dimensions from design plan
    length_u = 1219.2  # mm (along X)
    width_v = 2590.8   # mm (along Z, but v_dir is [0,0,-1], so magnitude is same)
    extrude_distance = 44.45  # mm (along Y)

    # Center the rectangle at origin for simplicity
    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .rect(length_u, width_v, centered=True)
        .extrude(extrude_distance)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108244_329b1876_0000\neg_03\iter_00/generated.step"
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
