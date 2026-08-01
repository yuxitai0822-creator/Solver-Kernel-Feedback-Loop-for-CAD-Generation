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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101269_f084ba14_0023\neg_03\iter_00\generated.step"

    # Design Plan dimensions (in mm):
    # Rectangle profile: u (x) = 95.25, v (z) = 571.5 (perturbed from 57.15 to 45.72? No, the perturbation description says 57.15 -> 45.72 but that seems to be a different dimension; the design plan says width_v = 571.5 which is 10x 57.15, so the perturbation likely affected the v-span. Let's use the design plan values: 95.25 x 571.5)
    # Extrude distance (w direction, y axis): 19.05

    # The frame has:
    # u_dir = [1,0,0] (x-axis)
    # v_dir = [0,0,-1] (negative z-axis)
    # w_dir = [0,1,0] (y-axis)
    # So the rectangle is in the XZ plane, extruded along Y.

    # Create the rectangle profile on the XZ plane
    # The rectangle spans from u=0 to u=95.25, v=0 to v=571.5 (in UV coordinates)
    # In world coordinates: u=x, v=-z (since v_dir = [0,0,-1])
    # So x from 0 to 95.25, z from -571.5 to 0

    # Build the part
    result = (
        cq.Workplane("XZ")
        .center(95.25/2, -571.5/2)  # center the rectangle
        .rect(95.25, 571.5)
        .extrude(19.05)  # extrude along Y (positive w direction)
    )

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
