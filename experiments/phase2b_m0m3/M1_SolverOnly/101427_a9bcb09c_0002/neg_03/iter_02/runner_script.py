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

    # Design Plan: extruded rectangle
    # Dimensions: length_u = 193.0 mm, width_v = 44.0 mm (perturbed from 55.0), extrude_distance = 50.0 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # The rectangle in UV space: (0,0) to (193,44) in UV, but note v_dir is [0,0,-1]
    # so the rectangle lies in the XZ plane (u along X, v along -Z).
    # Extrude along +w = +Y direction.

    # Build the rectangle on the XZ plane
    # Using Workplane("XZ") gives us X horizontal, Z vertical
    # We want a rectangle from (0,0) to (193,44) in UV space
    # U = X, V = -Z, so the rectangle corners in XYZ:
    # (0,0,0), (193,0,0), (193,0,-44), (0,0,-44)
    # But we can just use the Workplane rect method with centered=False

    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)  # start at origin
        .rect(193.0, 44.0, centered=False)  # width=193 along X, height=44 along Z
        .extrude(50.0)  # extrude along +Y (normal of XZ plane)
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双闭环反馈驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0002\neg_03\iter_02/generated.step"
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
