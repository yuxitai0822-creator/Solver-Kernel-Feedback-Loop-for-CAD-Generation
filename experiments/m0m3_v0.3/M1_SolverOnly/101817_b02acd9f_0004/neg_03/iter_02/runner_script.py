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

    # Design Plan: extruded rectangle plate
    # Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in UV plane: u from 7.83 to 127.83, v from -66.34 to -6.34
    # Note: The profile coordinates in the design plan are in UV space.
    # The rectangle spans 120.0 in u and 60.0 in v (scaled from cm to mm: 1200/10=120, 600/10=60).
    # The extrude direction is +w (positive Y in world).

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the profile lies in XZ)
    # The rectangle center in UV: u_center = (127.83 + 7.83)/2 = 67.83, v_center = (-66.34 + -6.34)/2 = -36.34
    # Width in u = 120.0, height in v = 60.0

    # Create workplane on XZ (since v_dir is Z, u_dir is X, normal is Y)
    result = (
        cq.Workplane("XZ")
        .center(67.83, -36.34)  # center of rectangle in UV (XZ plane)
        .rect(120.0, 60.0)      # width=120 (u), height=60 (v)
        .extrude(20.0)          # extrude along +Y (w direction)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0004\neg_03\iter_02\generated.step"
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
