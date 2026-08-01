import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_02\iter_00/generated.step"

    # Design parameters from the design plan
    # The stadium profile has:
    #   - straight_length = 500.0 mm (inferred from point span, but the curves show 50.0 mm straight? Let's check)
    #   - radius = 50.0 mm (from curve_field, but the perturbed radius is 6.25? Wait, the perturbation says radius changed from 5.0 to 6.25)
    # Actually looking at the curves:
    #   Arc1: center (0,0), radius 5.0, start 0, end 180
    #   Line1: (0, -5) to (50, -5)
    #   Arc2: center (50,0), radius 5.0, start 0, end 180
    #   Line2: (50, 5) to (0, 5)
    # So the straight length is 50.0 mm, radius is 5.0 mm
    # But the perturbation says radius changed from 5.0 to 6.25
    # Let's use the perturbed values: radius = 6.25, straight_length = 50.0
    # Extrude distance = 100.0 mm

    RADIUS = 6.25  # perturbed from 5.0
    STRAIGHT_LENGTH = 50.0
    EXTRUDE_DISTANCE = 100.0

    # Build the stadium profile
    # Start with the first arc at (0,0) going from 0 to 180 degrees (top half)
    # Then line from (0, -RADIUS) to (STRAIGHT_LENGTH, -RADIUS)
    # Then arc at (STRAIGHT_LENGTH, 0) from 0 to 180 degrees (bottom half)
    # Then line from (STRAIGHT_LENGTH, RADIUS) back to (0, RADIUS)

    # Using cadquery's Workplane to build the profile
    result = (
        cq.Workplane("XY")
        .moveTo(0, RADIUS)  # Start at top-left of the first arc
        .threePointArc(
            (RADIUS, 0),  # Midpoint of the arc (top of the circle)
            (0, -RADIUS)  # End of the arc
        )
        .lineTo(STRAIGHT_LENGTH, -RADIUS)  # Bottom line
        .threePointArc(
            (STRAIGHT_LENGTH + RADIUS, 0),  # Midpoint of the second arc
            (STRAIGHT_LENGTH, RADIUS)  # End of the second arc
        )
        .lineTo(0, RADIUS)  # Top line back to start
        .close()
        .extrude(EXTRUDE_DISTANCE)
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
