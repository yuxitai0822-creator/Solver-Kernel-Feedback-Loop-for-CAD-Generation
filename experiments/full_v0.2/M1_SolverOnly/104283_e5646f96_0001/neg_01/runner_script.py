import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create the base plate profile
    # The profile consists of a rectangle with a circular cutout
    # From the design plan, the outer profile is defined by:
    # - A vertical line from (0.9188, 1.7937) to (0.9188, 0.0)
    # - A horizontal line from (0.9188, 0.0) to (3.8000, 0.0)
    # - A vertical line from (3.7174, 1.7937) to (3.7174, 0.0)
    # - A circular arc centered at (2.3181, 1.7491) with radius 1.4
    # The inner cutout is a circle centered at (2.3181, 1.7491) with radius 1.25

    # Note: The coordinates in the design plan are in cm (converted to mm by factor 10)
    # But the plan says unit_conversion_applied: cm_to_mm (x10), so the values are already in mm

    # Build the outer profile using a workplane
    result = (
        cq.Workplane("XY")
        .moveTo(0.9188335453558412, 1.7936743887554851)
        .lineTo(0.9188335453558412, 0.0)
        .lineTo(3.8000000566244125, 0.0)
        .lineTo(3.7174115708793822, 0.0)  # This line seems redundant but follows the plan
        .lineTo(3.7174115708793822, 1.7936743887554851)
        # Close the profile with a circular arc
        .threePointArc(
            (2.3181225581176115, 1.7490620724718653 + 1.4),  # approximate point on arc
            (0.9188335453558412, 1.7936743887554851)
        )
        .close()
        .extrude(18.0)
    )

    # Now cut out the inner circle
    result = (
        result
        .faces(">Z")
        .workplane()
        .circle(1.2500000000000002)
        .cutThruAll()
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0001\\neg_01/generated.step")

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
