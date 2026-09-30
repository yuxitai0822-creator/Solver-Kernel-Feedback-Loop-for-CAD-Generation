import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a cylinder (extruded circle) based on the design plan.
    # The design plan specifies:
    # - Circle radius: 12.5 mm (from dimensions.profiles[0].radius, note the value is 12.5 after cm->mm conversion? Actually the plan says radius value 12.5, but the profile curves show radius 1.25 in UV? Let's check: The profile curves have radius 1.25, but dimensions say radius 12.5. The compiler notes mention cm_to_mm (x10). So the UV coordinates are in cm? Actually the profile curves radius is 1.25, but the explicit dimension says 12.5 mm. The plan says unit is mm, and the compiler notes say cm_to_mm (x10). So the original source was in cm, and the radius 1.25 cm = 12.5 mm. So we use 12.5 mm.
    # - Extrude distance: 75.0 mm
    # - The circle center in UV is [-15.0, 10.0] (from dimensions.profiles[0].center_uv). But the profile curves show center_uv [-1.5, 1.0] which is again cm? Actually the dimensions are in mm, so center is at (-15, 10) mm.
    # - The frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]. So the extrusion direction is +w = +x axis.
    # - The circle lies in the uv-plane (y-z plane), and extrudes along x.

    # Build the cylinder.
    # We'll create a circle at (y=-15, z=10) with radius 12.5, then extrude along x by 75.

    result = (
        cq.Workplane("YZ")
        .center(-15.0, 10.0)
        .circle(12.5)
        .extrude(75.0)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\104283_e5646f96_0000\neg_01/generated.step")

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
