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

    # Design Plan: stadium extrusion
    # Stadium profile: two arcs (radius=10mm) connected by two lines (straight_length=28mm)
    # Extrude 4.0mm in +w direction (which is +Y in world coordinates)
    # The profile lies in the XZ plane (u=x, v=z, w=y)

    # Build the stadium profile in the XZ plane
    # Arc centers at (10, 0) and (38, 0) in UV (XZ) coordinates
    # Radius = 10mm, straight length = 28mm (distance between centers = 28mm)

    # Use a clean approach: build the profile using two arcs and two lines
    # Start at the top-left of the left arc: (20, 0)
    # Go along left arc (counterclockwise) to bottom: (0, -10)
    # Line to bottom-right: (28, -10)
    # Go along right arc (counterclockwise) to top: (48, 0)
    # Line back to start: (20, 0)

    # Build the wire segment by segment using cadquery's built-in arc and line operations
    s = cq.Workplane("XZ")

    # Start at top of left arc: (20, 0)
    s = s.moveTo(20, 0)

    # Left arc: center (10, 0), radius 10, from 0 to 180 degrees (top to bottom)
    # Use three-point arc: start (20, 0), mid (10, 10), end (0, 0)
    s = s.threePointArc((10, 10), (0, 0))

    # Bottom line: from (0, -10) to (28, -10)
    s = s.lineTo(28, -10)

    # Right arc: center (38, 0), radius 10, from 0 to 180 degrees (bottom to top)
    # Use three-point arc: start (28, -10), mid (38, -10), end (48, 0)
    s = s.threePointArc((38, -10), (48, 0))

    # Top line: from (48, 0) to (20, 0)
    s = s.lineTo(20, 0)

    # Close the wire
    s = s.close()

    # Extrude in the +Y direction (which is +w in the design plan)
    result = s.extrude(4.0)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102295_86f842dd_0000\neg_03\iter_02\generated.step"
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
