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
    # Extruded rectangle: 279.4 mm x 50.8 mm, extruded 19.05 mm
    # Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
    # The rectangle is defined in UV space, then extruded along +w

    # Build the rectangle profile in the UV plane (XZ plane in world coords)
    # Rectangle corners in UV: (0,0), (27.94,0), (27.94,5.08), (0,5.08)
    # But dimensions say length_u=279.4, width_v=50.8 (scaled by 10 from cm)
    # The UV coordinates in the profile are given as 27.94 and 5.08, which are
    # 1/10 of the actual dimensions. This suggests the profile is defined in cm
    # and we need to scale by 10 to get mm.

    # Actually, looking at the design plan more carefully:
    # - length_u = 279.4 mm
    # - width_v = 50.8 mm
    # - The profile curves have start/end UV coordinates like (0,5.08) and (27.94,0)
    # - These UV values are 1/10 of the mm dimensions, suggesting the profile
    #   was defined in cm and converted to mm by scaling x10
    # - So we should use the UV values directly as mm (they already are mm after conversion)

    # Wait, 27.94 * 10 = 279.4, and 5.08 * 10 = 50.8. So the UV coordinates
    # are in cm and need to be multiplied by 10 to get mm.
    # But the compiler notes say "cm_to_mm (x10)" was applied.
    # So the UV values in the design plan are already in mm? No, they show 27.94 and 5.08,
    # which are the cm values. The dimensions show 279.4 and 50.8 which are mm.
    # So we need to scale the profile by 10.

    # Let's build the rectangle directly with the correct mm dimensions.
    # Rectangle: 279.4 mm x 50.8 mm, centered at origin in the XZ plane
    # Extrude along Y axis (w direction = [0,1,0]) by 19.05 mm

    # Create workplane on XZ plane (normal is Y axis)
    wp = cq.Workplane("XZ")

    # Create the rectangle centered at origin
    # The rectangle spans from -139.7 to 139.7 in X, and -25.4 to 25.4 in Z
    result = wp.rect(279.4, 50.8, centered=True).extrude(19.05)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0007\neg_01\iter_00/generated.step"
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
