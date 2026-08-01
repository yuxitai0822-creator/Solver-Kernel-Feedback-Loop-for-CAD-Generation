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

    # Design Plan: flat_plate_or_panel, extruded rectangle
    # Dimensions: length_u=2438.4 mm, width_v=1219.2 mm, extrude_distance=12.7 mm
    # Profile rectangle corners in UV: (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
    # Note: The design plan UV coordinates are in cm (121.92 cm = 1219.2 mm), but the plan says unit is mm.
    # The perturbation description says original=121.92, perturbed=97.536 (cm? mm? unclear).
    # The previous script used 1219.2 mm for the rectangle half-dimensions, which matches 121.92 cm.
    # However, the design plan explicitly states unit=mm and the UV coordinates are 121.92, -60.96 etc.
    # This is inconsistent: 121.92 mm would give a 243.84 mm plate, not 2438.4 mm.
    # The design plan dimensions say length_u=2438.4 mm, width_v=1219.2 mm.
    # The UV coordinates in the profile are half-dimensions: 121.92 and 60.96.
    # If unit is mm, then 2*121.92 = 243.84 mm, not 2438.4 mm.
    # This suggests the UV coordinates are in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm).
    # But 2*1219.2 = 2438.4 mm (length_u) and 2*609.6 = 1219.2 mm (width_v).
    # So the UV coordinates are actually in mm*10 (i.e., cm).
    # The perturbation says original=121.92, perturbed=97.536.
    # If original is 121.92 cm = 1219.2 mm, perturbed is 97.536 cm = 975.36 mm.
    # So the perturbed rectangle half-dimensions are (975.36, -487.68) etc.
    # The previous script used 1219.2 and 487.68, which matches the original.
    # The perturbation description says to replace with perturbed values.
    # So we use 975.36 and 487.68 for the half-dimensions.
    # But wait: the design plan says length_u=2438.4, width_v=1219.2.
    # The perturbation changes the rectangle size.
    # The perturbed half-dimensions: 975.36 mm (u) and 487.68 mm (v).
    # This gives length_u = 2*975.36 = 1950.72 mm, width_v = 2*487.68 = 975.36 mm.
    # The design plan validation expects 2438.4 and 1219.2, but the perturbation changes this.
    # We follow the perturbation description.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108412_8de2f9c3_0000\neg_03\iter_00/generated.step"

    # Build the plate
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(2*975.36, 2*487.68)  # perturbed dimensions: 1950.72 x 975.36 mm
        .extrude(12.7)  # thickness = 12.7 mm
    )

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
