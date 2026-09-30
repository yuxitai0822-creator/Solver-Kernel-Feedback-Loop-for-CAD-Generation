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

    # Design Plan: extruded rectangular frame
    # Outer rectangle: from (-2.5, 57.5) to (195.5, -2.5) in UV plane
    #   -> width = 195.5 - (-2.5) = 198.0, height = 57.5 - (-2.5) = 60.0
    # Inner rectangle: from (0.0, 55.0) to (193.0, 0.0)
    #   -> width = 193.0, height = 55.0
    # Extrude distance: 25.0 mm (from design plan, not the perturbed 37.5)
    # Frame axes: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
    # So sketch on XZ plane, extrude along Y

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0001\neg_01\iter_01\generated.step"

    # Build the outer rectangle
    result = (cq.Workplane("XZ")
        .moveTo(-2.5, 57.5)
        .lineTo(-2.5, -2.5)
        .lineTo(195.5, -2.5)
        .lineTo(195.5, 57.5)
        .close()
        .extrude(25.0)  # extrude along Y (positive direction)
    )

    # Cut the inner hole
    inner = (cq.Workplane("XZ")
        .moveTo(0.0, 55.0)
        .lineTo(0.0, 0.0)
        .lineTo(193.0, 0.0)
        .lineTo(193.0, 55.0)
        .close()
        .extrude(25.0)  # same extrusion depth
    )

    result = result.cut(inner)

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
