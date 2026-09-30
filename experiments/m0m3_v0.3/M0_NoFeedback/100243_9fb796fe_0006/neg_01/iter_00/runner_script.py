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

    # Design Plan: Drone Leg - square strut
    # Extruded rectangle with dimensions 19.0 x 19.0 x 130.0 mm
    # The profile is a rectangle in the XZ plane, extruded along Y

    # Profile coordinates from design plan (in mm, after cm->mm conversion)
    # Original coordinates were in cm, multiplied by 10 for mm
    # Rectangle corners in UV frame (U=X, V=Z):
    # (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
    # Width = 1.9 cm = 19 mm, Height = 1.9 cm = 19 mm

    # Convert to mm (already in mm from design plan)
    x_min = -58.27820137826746
    y_min = -13.940145769681571  # Z in our coordinate system
    x_max = -56.37820137826746
    y_max = -12.04014576968157   # Z in our coordinate system

    # Center of rectangle
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    width = x_max - x_min  # 1.9 mm? No, should be 19 mm
    height = y_max - y_min  # 1.9 mm? No, should be 19 mm

    # The design plan says dimensions are 19.0 x 19.0 x 130.0 mm
    # But the coordinates give 1.9 x 1.9 (in cm originally, now mm after conversion)
    # This is a discrepancy - the coordinates were in cm and converted to mm
    # So the actual rectangle size is 19 mm x 19 mm

    # Let's rebuild using the explicit dimensions from the design plan
    # Rectangle: 19.0 mm x 19.0 mm, extruded 130.0 mm along Y

    # Create workplane on XZ plane (Y is extrusion direction)
    result = (
        cq.Workplane("XZ")
        .rect(19.0, 19.0, centered=True)
        .extrude(130.0)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0006\neg_01\iter_00\generated.step"
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
