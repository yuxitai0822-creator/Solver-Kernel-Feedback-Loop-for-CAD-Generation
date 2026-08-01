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

    # Design Plan: ruler holder w/screw - disk with single extruded circle
    # Dimensions from design plan:
    #   Circle center: (5.080000162124634, 6.350000202655792) in UV frame
    #   Circle radius: 0.4711700000000002 (but note: dimensions section says radius=4.7117)
    #   Extrude distance: 12.192 mm
    # The design plan shows a single outer circle with no inner loops.
    # The previous script incorrectly added an inner loop (radius 0.5) which is not in the design plan.
    # Also, the center coordinates in the design plan's profiles section are (50.800002, 63.500002)
    # which is 10x the curves center - this is due to cm->mm conversion.
    # The curves center (5.08, 6.35) is in cm, so multiply by 10 for mm: (50.8, 63.5)
    # Radius: curves says 0.47117 cm = 4.7117 mm, dimensions says 4.7117 mm - consistent.

    # Build the part according to design plan:
    # - Single outer circle at (50.8, 63.5) with radius 4.7117 mm
    # - Extrude 12.192 mm in +w direction (which is +Y in our frame)
    # - No inner holes

    # Create workplane on XZ plane (as in original), but extrude along Y
    wp = cq.Workplane("XZ")

    # Create the outer circle
    center_x = 50.800002
    center_y = 63.500002
    radius = 4.7117

    # Build the circle and extrude
    result = wp.moveTo(center_x, center_y).circle(radius).extrude(12.192)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0003\neg_03\iter_00/generated.step"
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
