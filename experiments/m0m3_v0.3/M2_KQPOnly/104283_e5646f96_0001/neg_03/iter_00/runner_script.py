import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0001\neg_03\iter_00\generated.step"

    # Design Plan Interpretation:
    # - Two profiles (outer rings) that share a common circle feature
    # - Profile 1: rectangle with a circular arc on one side
    # - Profile 2: rectangle with a circular hole (inner circle)
    # - Extrude 18.0 mm in +Z direction
    # - The geometry is essentially a rectangular block with a circular end and a through hole

    # Build the base shape (profile 1): a rectangle with a circular arc on the right side
    # The rectangle spans from x=0.9188 to x=3.8000 in u, and y=0 to y=1.7937 in v
    # But the circle center is at (2.3181, 1.7491) with radius 1.4
    # This creates a shape like a rectangle with a circular cap

    # Let's build this as a 2D sketch and extrude
    result = (
        cq.Workplane("XY")
        # Start at bottom-left corner of the rectangle
        .moveTo(0.9188335453558412, 0.0)
        # Line to bottom-right
        .lineTo(3.8000000566244125, 0.0)
        # Line up to the circle tangent point
        .lineTo(3.7174115708793822, 1.7936743887554851)
        # Arc to the left side (circle center at 2.3181, 1.7491, radius 1.4)
        # The arc goes from right side to left side
        .threePointArc(
            (2.3181225581176115, 1.7490620724718653 + 1.4),  # top of circle
            (0.9188335453558412, 1.7936743887554851)  # left side point
        )
        # Line back down to start
        .lineTo(0.9188335453558412, 0.0)
        .close()
        # Extrude 18.0 mm
        .extrude(18.0)
    )

    # Now cut the inner hole (profile 2 inner ring)
    # The hole is a circle centered at (2.3181, 1.7491) with radius 1.25
    hole = (
        cq.Workplane("XY")
        .moveTo(2.3181225581176115, 1.7490620724718653)
        .circle(1.2500000000000002)
        .extrude(18.0)
    )

    result = result.cut(hole)

    # Export
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
