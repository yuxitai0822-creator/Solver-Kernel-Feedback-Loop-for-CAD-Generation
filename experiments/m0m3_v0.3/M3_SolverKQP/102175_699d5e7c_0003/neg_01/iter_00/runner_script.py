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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

    # Design Plan: rectangular prism 39.0 x 68.0 x 10.0 mm
    # The profile is a rectangle with corners at (-3.9, 6.8) and (0.0, 0.0) in UV space
    # After unit conversion (cm->mm x10): width = 39.0 mm, height = 68.0 mm
    # Extrude distance = 10.0 mm (converted from 1.0 cm)

    # Build the rectangle centered at the midpoint of the given corners
    x_min = -3.9 * 10  # -39.0
    x_max = 0.0 * 10   # 0.0
    y_min = 0.0 * 10   # 0.0
    y_max = 6.8 * 10   # 68.0

    width = x_max - x_min   # 39.0 mm
    height = y_max - y_min  # 68.0 mm
    center_x = (x_min + x_max) / 2  # -19.5
    center_y = (y_min + y_max) / 2  # 34.0

    # Create the rectangular prism
    result = (
        cq.Workplane("XY")
        .moveTo(center_x, center_y)
        .rect(width, height, centered=True)
        .extrude(10.0)  # 10.0 mm as specified
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
