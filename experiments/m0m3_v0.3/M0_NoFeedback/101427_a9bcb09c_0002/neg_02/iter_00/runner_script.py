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
    # Dimensions: length_u = 1930.0 mm, width_v = 550.0 mm, extrude_distance = 50.0 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # The rectangle is defined in UV space, then extruded along +w (Y axis)

    # Build the rectangle in the XZ plane (since v_dir is -Z, u_dir is X)
    # Rectangle corners in UV: (0,0), (193,0), (193,55), (0,55)
    # But note: dimensions are in mm, and the design plan says length_u=1930.0, width_v=550.0
    # The curves show 193.0 and 55.0, but the dimensions say 1930.0 and 550.0
    # This is because the compiler notes say unit_conversion_applied: cm_to_mm (x10)
    # So the curves are in cm, but we need to output in mm
    # The curves show 193.0 and 55.0, which become 1930.0 and 550.0 after conversion
    # So we use the converted values: 1930.0 x 550.0 x 50.0

    # Create workplane on XZ plane (since v_dir = [0,0,-1], the sketch plane is XZ)
    # The rectangle is centered at origin for simplicity
    wp = cq.Workplane("XZ")

    # Create rectangle centered at origin
    # Width along X (u_dir) = 1930.0, height along Z (v_dir) = 550.0
    result = wp.rect(1930.0, 550.0, centered=True).extrude(50.0)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0002\neg_02\iter_00/generated.step"
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
