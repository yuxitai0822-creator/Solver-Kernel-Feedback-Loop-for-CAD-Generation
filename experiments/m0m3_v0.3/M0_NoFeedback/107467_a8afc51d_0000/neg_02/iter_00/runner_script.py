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

    # Design Plan: single disk (extruded circle)
    # - Circle radius: 3.0 mm (from dimensions.profiles[0].radius.value)
    # - Extrude distance: 14.0 mm (from dimensions.extrude_distance.value)
    # - The perturbed radius 0.375 is for the sketch profile radius (the circle radius in the profile curves)
    #   but the design plan says the profile radius is 3.0 mm. The perturbation description says
    #   original=0.30000000000000004, perturbed=0.37500000000000006. This is the radius of the circle
    #   in the profile curves (the sketch circle). The design plan's dimensions.profiles[0].radius.value
    #   is 3.0, which is the overall part radius. The profile curve radius is 0.375 (perturbed).
    #   Wait: The design plan says radius=0.30000000000000004 in the curves, and dimensions.profiles[0].radius.value=3.0.
    #   This is confusing. Let's re-read: The design plan has:
    #     profiles[0].rings[0].curves[0].radius = 0.30000000000000004
    #     dimensions.profiles[0].radius.value = 3.0
    #   The perturbation says original=0.30000000000000004, perturbed=0.37500000000000006.
    #   So the sketch circle radius is 0.375 mm (perturbed). The extrude distance is 14.0 mm.
    #   The part should be a cylinder with radius 0.375 mm and height 14.0 mm.
    #   But the validation intents expect span_u=6.0, span_v=6.0, which would be for radius 3.0.
    #   This is a negative perturbation: the radius is changed from 3.0 to 0.375.
    #   The design plan's dimensions.profiles[0].radius.value=3.0 is the original, but the perturbation
    #   changes the curve radius to 0.375. So we use the perturbed value.
    #   The validation intents will fail (expected 6.0 span, but actual will be 0.75), but that's
    #   the point of negative perturbation.

    # Build the part
    result = (
        cq.Workplane("XY")
        .circle(0.375)  # perturbed radius
        .extrude(14.0)   # extrude distance
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0000\neg_02\iter_00\generated.step"
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
