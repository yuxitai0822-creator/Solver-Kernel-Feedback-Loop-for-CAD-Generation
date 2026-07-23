import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    # Stadium parameters (unit conversion applied: cm to mm)
    # The profile curves define a stadium with radius 1.0 and straight length 2.8 in local units.
    # After cm_to_mm conversion, radius = 10.0 mm, straight_length = 28.0 mm.
    # Total span along u = 2*radius + straight_length = 48.0 mm.
    # Total span along v = 2*radius = 20.0 mm.

    radius = 10.0
    straight_length = 28.0
    extrude_distance = 4.0

    # Build the stadium profile on the XZ plane (u=X, v=-Z, w=Y)
    # The stadium center is at (radius, 0) in the local 2D frame.
    # In the XZ plane, this maps to X=radius, Z=0.
    # The extrusion direction +w maps to +Y.

    result = (
        cq.Workplane("XZ")
        .center(radius, 0)
        .slot2D(straight_length, radius, 0)  # slot2D(length, diameter, angle)
        .extrude(extrude_distance)
    )

    # Export the result to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\102295_86f842dd_0000\ex2/generated.step"
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
