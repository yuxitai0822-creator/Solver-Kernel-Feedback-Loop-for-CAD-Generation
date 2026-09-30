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

    # Design parameters from the design plan
    # Note: The perturbation description indicates the outer radius was changed from 0.55372 to 0.69215 (in cm)
    # After unit conversion (cm to mm, x10): outer radius = 0.69215 * 10 = 6.9215 mm
    OUTER_RADIUS = 6.9215  # mm (perturbed from 0.55372 cm to 0.69215 cm, then *10)
    INNER_RADIUS = 1.9812  # mm (original: 0.19812 cm * 10)
    CENTER_X = -25.40000081062317  # mm (original: -2.540000081062317 cm * 10)
    CENTER_Y = 12.700000405311584  # mm (original: 1.2700000405311584 cm * 10)
    EXTRUDE_DISTANCE = 1.3208  # mm (original: 0.13208 cm * 10)

    # Output path
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0004\neg_02\iter_02/generated.step"

    # Build the washer using cadquery
    # Create a workplane on the XY plane (default)
    result = (
        cq.Workplane("XY")
        .moveTo(CENTER_X, CENTER_Y)
        .circle(OUTER_RADIUS)
        .extrude(EXTRUDE_DISTANCE)
        .faces(">Z")  # Select the top face
        .workplane()
        .hole(INNER_RADIUS * 2, EXTRUDE_DISTANCE)  # Through hole
    )

    # Export to STEP
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
