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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0003\neg_01\iter_00/generated.step"

    # Design Plan parameters:
    # - Circle center at (16.994660913961006, 17.998556732836484) in UV plane
    # - Circle radius = 25.4 mm (from dimensions.radius.value)
    # - Extrude distance = 8.89 mm (from extrude.distance_total.value)
    # - The profile center_uv is given as [16.994661, 17.998557] which matches
    # - The circle in profiles.rings.curves has center_uv [1.6994660913961006, 1.7998556732836484] and radius 2.54
    #   BUT the dimensions section says radius=25.4 and center_uv=[16.994661, 17.998557]
    #   The compiler note says unit_conversion_applied: cm_to_mm (x10)
    #   So the original values were in cm: radius 2.54 cm = 25.4 mm, center (1.699466, 1.799856) cm = (16.99466, 17.99856) mm
    #   The dimensions section already has the mm-converted values.
    # - Extrude distance: 8.89 mm (from extrude.distance_total.value)
    # - The perturbation description says: operator=E2_extrude_depth; original=0.8889999999999999; perturbed=1.3335
    #   This is in cm? original 0.889 cm = 8.89 mm, perturbed 1.3335 cm = 13.335 mm
    #   The previous script used EXTENT_TOTAL_MM = 13.334999999999999 which matches the perturbed value.
    #   But the Design Plan says extrude distance = 8.89 mm (the original, unperturbed value).
    #   Since this is iteration 0 and the perturbation description says "TODO: replace with negative CAD code",
    #   we should follow the Design Plan which specifies 8.89 mm.

    # Build the part:
    # 1. Create a workplane on XY
    # 2. Draw a circle at (16.99466, 17.99856) with radius 25.4
    # 3. Extrude by 8.89 mm in +Z direction

    result = (
        cq.Workplane("XY")
        .moveTo(16.994660913961006, 17.998556732836484)
        .circle(25.4)
        .extrude(8.89)
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
