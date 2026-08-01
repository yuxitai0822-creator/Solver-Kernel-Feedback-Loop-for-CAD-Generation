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
    # Extruded rectangle: 171.45 mm x 38.1 mm, extruded 6.35 mm
    # The profile is defined in UV space where:
    #   u_dir = [1.0, 0.0, 0.0] (X axis)
    #   v_dir = [0.0, 0.0, -1.0] (negative Z axis)
    #   w_dir = [0.0, 1.0, 0.0] (Y axis)
    # The rectangle corners in UV: (0,0), (17.145,0), (17.145,3.81), (0,3.81)
    # Note: The design plan dimensions are length_u=171.45, width_v=38.1
    # The UV coordinates appear to be in cm (17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm)
    # So we multiply by 10 to convert to mm.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108850_0dcd5ef1_0002\neg_03\iter_00\generated.step"

    # Build the rectangle in the XZ plane (since v_dir is -Z, u_dir is X)
    # The rectangle is 171.45 mm along X, 38.1 mm along Z (negative direction)
    # We'll create it centered at origin for simplicity

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Rectangle dimensions in mm
    length_u = 171.45  # along X
    width_v = 38.1     # along Z (but v_dir is -Z, so we use positive Z for the rect)

    # Create the rectangle centered at origin
    # The rectangle spans from -length_u/2 to +length_u/2 in X
    # and from -width_v/2 to +width_v/2 in Z
    result = wp.center(0, 0).rect(length_u, width_v).extrude(6.35)

    # Export
    importers = None
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
