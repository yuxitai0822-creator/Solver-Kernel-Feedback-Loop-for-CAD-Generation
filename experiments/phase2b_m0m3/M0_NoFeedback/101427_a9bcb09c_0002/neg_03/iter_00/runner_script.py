import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: extruded rectangle
    # Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
    # Note: The design plan states dimensions in mm, but the original source had cm->mm conversion.
    # The plan explicitly says length_u=1930.0? Wait, let's re-read.
    # The design plan says: length_u value=1930.0, width_v value=550.0, extrude_distance=50.0
    # But the perturbation description says original=55.0, perturbed=44.0 (this is the width_v?)
    # Actually the plan says width_v=550.0 (which is 55.0 cm converted to mm? No, it says unit=mm)
    # Let's check: The plan says unit_conversion_applied: cm_to_mm (x10)
    # So original was 55.0 cm = 550 mm, but perturbation says original=55.0 perturbed=44.0
    # This is confusing. Let's just follow the design plan exactly as given.
    # The plan says: length_u=1930.0, width_v=550.0, extrude=50.0
    # But the perturbation says original=55.0, perturbed=44.0 (this is the width in cm?)
    # Actually the perturbation description says "operator=E1_envelope; original=55.0; perturbed=44.0"
    # This likely refers to the width_v dimension being changed from 55.0 to 44.0 (in cm? or mm?)
    # The plan says width_v=550.0 (mm), but the perturbation says original=55.0, perturbed=44.0
    # Since the plan says unit_conversion_applied: cm_to_mm (x10), the original was 55.0 cm = 550 mm
    # The perturbation changes it to 44.0 cm = 440 mm? Or directly to 44.0 mm?
    # The perturbation description is ambiguous. Let's use the design plan values directly.
    # The plan says width_v=550.0, so we use that.

    # Actually, looking more carefully at the design plan:
    # "profiles": [{"length_u": {"value": 1930.0}, "width_v": {"value": 550.0}}]
    # "extrude_distance": {"value": 50.0}
    # These are the target dimensions.

    # But the perturbation says "original=55.0; perturbed=44.0" - this is likely the width_v in cm
    # So the perturbed width_v should be 44.0 cm = 440 mm? Or 44.0 mm?
    # The plan says unit_conversion_applied: cm_to_mm (x10), so original 55.0 cm -> 550 mm
    # Perturbed would be 44.0 cm -> 440 mm? Or just 44.0 mm?
    # The perturbation description says "original=55.0; perturbed=44.0" without units.
    # Since the plan's original width_v is 550.0 mm (which is 55.0 cm * 10), 
    # the perturbed value should be 44.0 * 10 = 440.0 mm? Or just 44.0 mm?
    # This is unclear. Let's just use the design plan values as-is: width_v=550.0

    # Actually, re-reading: "Perturbation description (TODO: replace with negative CAD code):
    # operator=E1_envelope; original=55.0; perturbed=44.0 (see TODO: negative CAD code not yet wired)"
    # This is a placeholder. The actual negative CAD code is not wired yet.
    # So we should just follow the design plan exactly.

    # The design plan says:
    # - Rectangle in UV space: start (0,55) -> (0,0) -> (193,0) -> (193,55) -> (0,55)
    # - But then dimensions say length_u=1930.0, width_v=550.0
    # - The curves use values 0, 55, 193 - these are in cm? Or mm?
    # - The unit_conversion_applied says cm_to_mm (x10), so the curves are in cm?
    # - 193 cm = 1930 mm, 55 cm = 550 mm. Yes, that matches.
    # - So the rectangle is 1930 mm x 550 mm, extruded 50 mm.

    # Let's build it simply:

    result = (
        cq.Workplane("XY")
        .rect(1930.0, 550.0, centered=True)
        .extrude(50.0)
    )

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0002\neg_03\iter_00/generated.step"
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
