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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0009\neg_02\iter_00\generated.step"

    # Design Plan dimensions (in mm, converted from cm)
    # Rectangle: length_u = 209.55 mm, width_v = 57.912 mm
    # Extrude distance = 19.05 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means: u = X, v = -Z, w = Y
    # So the rectangle lies in the X-Z plane (since u and v are X and -Z)
    # and extrudes along Y (w direction)

    # Build the rectangle in the XZ plane
    # The rectangle spans from (0,0) to (209.55, 57.912) in UV coordinates
    # U maps to X, V maps to -Z (so V=0 -> Z=0, V=57.912 -> Z=-57.912)
    # But we want the rectangle to be centered or positioned appropriately
    # The design plan shows start_uv at (0, 5.7912) and end_uv at (20.955, 0) etc.
    # Note: the original had 20.955 which is 209.55/10 (cm to mm conversion issue)
    # The perturbed value is 25.145999999999997 which is 209.55/10 * 1.2 = 25.146
    # But the design plan says length_u = 209.55, so we use that directly

    # Create the rectangle in the XZ plane
    # We'll create a workplane on XZ and draw the rectangle
    result = (
        cq.Workplane("XZ")
        .center(209.55/2, -57.912/2)  # center the rectangle
        .rect(209.55, 57.912)
        .extrude(19.05)  # extrude along Y (positive Y direction)
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
