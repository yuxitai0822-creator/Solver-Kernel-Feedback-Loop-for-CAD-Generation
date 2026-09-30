import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_03\iter_02\generated.step"

    # Design parameters from the design plan
    # The plan's dimensions section is authoritative:
    # straight_length=500.0, radius=50.0, extrude_distance=100.0
    # The total span along u should be straight_length + 2*radius = 500 + 100 = 600
    # The total span along v should be 2*radius = 100
    straight_length = 500.0
    radius = 50.0
    extrude_distance = 100.0

    # Build the stadium profile using native cadquery arc and line operations
    # This ensures proper geometry rather than discretized points

    # Create workplane
    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(0, -radius)  # Start at bottom of left semicircle
        .threePointArc((radius, 0), (0, radius))  # Left semicircle (bottom to top)
        .lineTo(straight_length, radius)  # Top line
        .threePointArc((straight_length + radius, 0), (straight_length, -radius))  # Right semicircle (top to bottom)
        .lineTo(0, -radius)  # Bottom line back to start
        .close()
        .extrude(extrude_distance)
    )

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
