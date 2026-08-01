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

    # Design Plan: MPPF_FrameBottom1 4x6 v1
    # Extruded rectangle: 171.45 x 38.1 x 6.35 mm
    # The design plan specifies a rectangle in UV space:
    #   u: 0 to 17.145 (but note: unit conversion cm->mm, so 17.145 cm = 171.45 mm)
    #   v: 0 to 3.81 (3.81 cm = 38.1 mm)
    # Extrude distance: 6.35 mm in +w direction
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means: u = X, v = -Z, w = Y
    # So the rectangle lies in the XZ plane (since u and v span X and Z)
    # and extrudes along Y (w direction).

    # Build the rectangle in the XZ plane
    # The rectangle corners in UV: (0,0), (171.45,0), (171.45,38.1), (0,38.1)
    # In XYZ: u->X, v->-Z, so:
    #   (0,0) -> (0, 0, 0)
    #   (171.45,0) -> (171.45, 0, 0)
    #   (171.45,38.1) -> (171.45, 0, -38.1)
    #   (0,38.1) -> (0, 0, -38.1)

    # Create workplane on XZ plane (normal = Y)
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at (171.45/2, -38.1/2) in XZ plane
    # Width along X = 171.45, Height along Z = 38.1
    result = wp.center(171.45/2, -38.1/2).rect(171.45, 38.1, centered=True).extrude(6.35)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108850_0dcd5ef1_0002\neg_02\iter_00\generated.step"
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
