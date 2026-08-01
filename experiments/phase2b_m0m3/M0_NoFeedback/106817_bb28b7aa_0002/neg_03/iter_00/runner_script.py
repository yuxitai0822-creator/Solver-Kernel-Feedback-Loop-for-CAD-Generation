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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

    # Design Plan parameters:
    # - Circle center at (11.430000364780426, 0.0) in UV frame
    # - Circle radius = 4.87045 mm (from dimensions.profiles[0].radius)
    # - Extrude distance = 6.8707 mm along +w direction
    # - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # - The profile center_uv is given as [11.430000364780426, 0.0] but the radius is 4.87045
    # - The outer ring has radius 0.48704499999999984 which seems like a mistake (too small)
    # - Using the explicit dimension radius = 4.87045 mm

    # Build the part: a simple disk (extruded circle)
    # Workplane is XZ (since v_dir = [0,0,-1] means v is along -Z, w is along Y)
    # We'll create the circle on the XZ plane and extrude along Y

    result = (
        cq.Workplane("XZ")
        .circle(4.87045)  # radius from explicit dimension
        .extrude(6.8707)   # extrude distance along Y (which is +w direction)
    )

    exporters.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
