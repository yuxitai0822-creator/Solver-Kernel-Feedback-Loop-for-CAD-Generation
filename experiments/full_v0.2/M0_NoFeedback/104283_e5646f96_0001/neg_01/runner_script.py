import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create the base plate (outer profile)
    # The outer profile is defined by two vertical lines and a circular arc at the top
    # Points from the design plan (in mm, converted from cm):
    # Start at (0.9188335453558412, 0.0)
    # Line up to (0.9188335453558412, 1.7936743887554851)
    # Arc (circle) center at (2.3181225581176115, 1.7490620724718653) radius 1.4
    # Line down from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
    # Close the profile

    # Build the outer profile as a wire
    outer_wire = (
        cq.Workplane("XY")
        .moveTo(0.9188335453558412, 0.0)
        .lineTo(0.9188335453558412, 1.7936743887554851)
        .threePointArc(
            (2.3181225581176115, 1.7490620724718653 + 1.4),  # top of arc
            (3.7174115708793822, 1.7936743887554851)
        )
        .lineTo(3.7174115708793822, 0.0)
        .close()
        .wire()
    )

    # Create the inner hole (circle)
    inner_center = (2.3181225581176115, 1.7490620724718653)
    inner_radius = 1.2500000000000002

    # Build the full profile with hole
    result = (
        cq.Workplane("XY")
        .placeSketch(outer_wire)
        .circle(inner_center[0], inner_center[1], inner_radius)  # hole
        .extrude(18.0)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0001\\neg_01/generated.step")

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
