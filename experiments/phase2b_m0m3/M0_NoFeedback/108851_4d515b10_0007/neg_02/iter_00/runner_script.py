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

    # Design Plan: SoapCutterBackBar1 v1
    # Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle in UV plane: u from 0 to 27.94, v from 0 to 5.08
    # Note: Design plan dimensions are in cm, converted to mm (x10)
    #   length_u = 279.4 mm (27.94 cm * 10)
    #   width_v = 50.8 mm (5.08 cm * 10)
    #   extrude_distance = 19.05 mm (1.905 cm * 10)

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0007\neg_02\iter_00\generated.step"

    # Build the rectangle profile in the UV plane
    # UV coordinates: u from 0 to 27.94, v from 0 to 5.08
    # But the design plan says length_u=279.4, width_v=50.8 (these are the actual dimensions)
    # The profile curves show u from 0 to 27.94, v from 0 to 5.08 (these are in cm?)
    # Actually the design plan says unit conversion cm_to_mm (x10) was applied
    # So the profile coordinates are already in mm? Let's check:
    #   curves: start_uv [0, 5.08] -> [0, 0] -> [27.94, 0] -> [27.94, 5.08] -> [0, 5.08]
    #   This gives width = 27.94 mm, height = 5.08 mm
    #   But dimensions say length_u=279.4, width_v=50.8
    #   The compiler note says cm_to_mm (x10) was applied
    #   So original was 2.794 cm x 0.508 cm, converted to 27.94 mm x 5.08 mm
    #   But the dimensions say 279.4 x 50.8... that's 10x larger
    #   Let me re-read: the profile curves are in UV space, and the dimensions are the actual part dimensions
    #   The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    #   So the rectangle in UV plane is 27.94 x 5.08, but the part dimensions are 279.4 x 50.8
    #   This means the UV coordinates are scaled by 10x to get actual dimensions
    #   Actually, looking more carefully: the profile curves show start_uv [0, 5.08] etc.
    #   These are the UV coordinates of the profile. The dimensions say length_u=279.4, width_v=50.8
    #   So the profile in UV space is 27.94 x 5.08, but the actual part is 279.4 x 50.8
    #   This is a 10x scaling. The compiler note says cm_to_mm (x10) was applied.
    #   So the original design was 27.94 cm x 5.08 cm = 279.4 mm x 50.8 mm
    #   The profile curves are in cm, and we need to scale by 10 to get mm
    #   OR the profile curves are already in mm and the dimensions are wrong?
    #   Let me just use the dimensions directly: 279.4 x 50.8 x 19.05

    # Create the workplane on XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # Actually, with u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]:
    #   The sketch plane is defined by u and v axes, so it's the XZ plane
    #   Extrude direction is +w = +Y

    # Build the rectangle centered at origin
    result = (
        cq.Workplane("XZ")
        .rect(279.4, 50.8, centered=True)
        .extrude(19.05)
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
