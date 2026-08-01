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

    # Design Plan: basic slat v1 (5)
    # Extruded rectangle with dimensions:
    #   length_u = 95.25 mm (along u-axis = x)
    #   width_v = 571.5 mm (along v-axis = z, since v_dir = [0,0,-1])
    #   extrude_distance = 19.05 mm (along w-axis = y)
    #
    # The profile rectangle in UV coordinates:
    #   u: 0.0 to 9.525 (but note: the curves define a rectangle with u-span = 9.525)
    #   v: 0.0 to 57.15
    # However, the dimensions say length_u = 95.25 and width_v = 571.5.
    # The UV coordinates in the profile are scaled by a factor of 10?
    # Actually, looking at the curves:
    #   start_uv: (9.525, 57.15) to (9.525, 0.0)  -> u=9.525, v from 57.15 to 0
    #   (0.0, 57.15) to (9.525, 57.15) -> u from 0 to 9.525, v=57.15
    #   (0.0, 0.0) to (0.0, 57.15) -> u=0, v from 0 to 57.15
    #   (9.525, 0.0) to (0.0, 0.0) -> u from 9.525 to 0, v=0
    # So the rectangle spans u: [0, 9.525] and v: [0, 57.15].
    # But the dimensions say length_u = 95.25 and width_v = 571.5.
    # 95.25 / 9.525 = 10, 571.5 / 57.15 = 10. So the UV coordinates are in cm, and we need to scale by 10 to get mm.
    # The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
    # So the actual rectangle in mm is: u: [0, 95.25], v: [0, 571.5].
    #
    # The frame:
    #   u_dir = [1, 0, 0]  (x-axis)
    #   v_dir = [0, 0, -1] (negative z-axis)
    #   w_dir = [0, 1, 0]  (y-axis)
    # So the rectangle lies in the XZ plane (u=x, v=-z), and extrudes along y.
    #
    # We'll build a rectangle centered at (95.25/2, 571.5/2) in the XZ plane, then extrude.

    # Dimensions in mm
    length_u = 95.25  # along x
    width_v = 571.5   # along z (positive v_dir is [0,0,-1], so v=0..571.5 maps to z=0..-571.5)
    extrude_dist = 19.05  # along y

    # Build the rectangle on the XZ plane (Y is normal)
    # The rectangle spans x: [0, 95.25], z: [-571.5, 0] (since v_dir = [0,0,-1], v=0 -> z=0, v=571.5 -> z=-571.5)
    # We'll center it for convenience, then translate if needed.
    # Actually, let's just build it at the origin and then translate.

    # Create workplane on XZ (Y normal)
    wp = cq.Workplane("XZ")

    # Build the rectangle: center at (length_u/2, -width_v/2) in XZ coordinates
    # The rectangle spans x: [0, length_u], z: [-width_v, 0]
    # Center = (length_u/2, -width_v/2)
    center_x = length_u / 2.0
    center_z = -width_v / 2.0

    # Create the rectangle
    result = wp.moveTo(center_x, center_z).rect(length_u, width_v, centered=True).extrude(extrude_dist)

    # Export to STEP
    exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101269_f084ba14_0023\neg_02\iter_00/generated.step")

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
