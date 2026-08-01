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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0002\neg_02\iter_00/generated.step"

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: corners at (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88) in UV plane
    # Inner rectangle: corners at (-6.0, 11.0), (-2.0, 11.0), (-2.0, 15.0), (-6.0, 15.0) in UV plane
    # Frame axes: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
    # Extrude distance: 1120.0 mm along -w direction (i.e., negative X)

    # Build on YZ plane (since w_dir is X, and we extrude along -X)
    # The UV coordinates map to YZ plane: u -> Z, v -> Y
    # Outer rectangle in YZ: Z from -6.12 to -1.88, Y from 10.88 to 15.12
    # Inner rectangle in YZ: Z from -6.0 to -2.0, Y from 11.0 to 15.0

    # Create outer rectangle on YZ plane
    result = (
        cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(-1.88, 10.88)  # Z, Y coordinates
        .lineTo(-1.88, 15.12)
        .lineTo(-6.12, 15.12)
        .lineTo(-6.12, 10.88)
        .close()
        .extrude(1120.0)  # extrude along +X (positive w direction)
    )

    # Cut inner hole: create inner rectangle and extrude through
    inner = (
        cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(-2.0, 11.0)  # Z, Y coordinates
        .lineTo(-2.0, 15.0)
        .lineTo(-6.0, 15.0)
        .lineTo(-6.0, 11.0)
        .close()
        .extrude(1120.0)
    )

    result = result.cut(inner)

    # Export
    cq.exporters.export(result, OUT_STEP_PATH)

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
