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

    # Design Plan: Backing v1 - flat rectangular plate
    # Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm
    # The perturbation changes the y-dimension from 215.9 to 17.272 (but we follow the design plan)
    # Actually, looking at the design plan, the width_v is 215.9, but the perturbation description says
    # original=21.59, perturbed=17.272. This suggests the perturbation is on a different scale.
    # The design plan explicitly states width_v = 215.9 (which is 21.59 * 10, consistent with cm->mm conversion).
    # The perturbation changes 21.59 to 17.272, so in mm that would be 172.72.
    # However, the design plan's explicit dimension is 215.9, so we must follow the design plan.
    # The previous script used 194.31 and 21.59 which doesn't match the design plan.
    # We'll create a clean script matching the design plan exactly.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0001\neg_03\iter_00/generated.step"

    # Create the rectangular plate
    # Using the design plan dimensions:
    # length_u = 279.4 mm (along x)
    # width_v = 215.9 mm (along y)
    # extrude_distance = 1.5875 mm (along z)

    result = (
        cq.Workplane("XY")
        .rect(279.4, 215.9, centered=True)
        .extrude(1.5875)
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
