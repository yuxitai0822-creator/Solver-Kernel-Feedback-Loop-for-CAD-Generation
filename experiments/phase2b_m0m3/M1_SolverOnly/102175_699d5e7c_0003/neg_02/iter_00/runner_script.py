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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102175_699d5e7c_0003\neg_02\iter_00\generated.step"

    # Design Plan dimensions (in mm, after cm->mm conversion):
    # Rectangle: length_u = 39.0 mm, width_v = 68.0 mm
    # Extrude distance: 10.0 mm
    # The profile coordinates in the design plan are given in UV space:
    #   start_uv = (-3.9, 6.8), end_uv = (0.0, 6.8) etc.
    # These define a rectangle of width 3.9 and height 6.8 in UV space.
    # But the explicit dimensions say length_u=39.0, width_v=68.0.
    # The UV coordinates appear to be in cm (since 3.9 cm = 39 mm, 6.8 cm = 68 mm).
    # So we scale the UV coordinates by 10 to get mm.

    # Build the rectangle in the XY plane (z=0), centered at origin for simplicity.
    # Rectangle dimensions: 39.0 mm along X (u direction), 68.0 mm along Y (v direction).
    # Extrude 10.0 mm in +Z direction.

    result = (
        cq.Workplane("XY")
        .rect(39.0, 68.0, centered=True)
        .extrude(10.0)
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
