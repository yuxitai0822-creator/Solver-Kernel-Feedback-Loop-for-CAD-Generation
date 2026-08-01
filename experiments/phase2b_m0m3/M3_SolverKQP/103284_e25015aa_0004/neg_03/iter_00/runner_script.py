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

    # Design Plan: Tail Stock Lever - a simple disk (extruded circle)
    # Dimensions:
    #   Radius: 11.938 mm (from profiles[0].radius.value)
    #   Extrude distance: 12.7 mm (from extrude.distance_total.value)
    #   Center UV: (8.077681, 8.284339) - used for positioning
    #
    # The previous script had issues:
    # 1. It tried to load a history JSON file that may not exist
    # 2. It had complex multi-loop logic for a simple disk
    # 3. It incorrectly included an inner loop (hole) when the design plan specifies only an outer circle
    # 4. The OUT_STEP path was not properly set
    #
    # This script creates a simple cylinder (extruded circle) matching the design plan.

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0004\neg_03\iter_00\generated.step"

    # Parameters from design plan
    radius = 11.938  # mm
    height = 12.7    # mm
    center_x = 8.077681
    center_y = 8.284339

    # Build the part: a simple disk (cylinder)
    result = (
        cq.Workplane("XY")
        .moveTo(center_x, center_y)
        .circle(radius)
        .extrude(height)
    )

    # Export to STEP
    importers.export(result, OUT_STEP_PATH)

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
