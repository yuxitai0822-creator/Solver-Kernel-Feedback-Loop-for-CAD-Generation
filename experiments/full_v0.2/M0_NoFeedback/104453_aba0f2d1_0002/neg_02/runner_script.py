import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Build the stadium profile
    # The stadium consists of two arcs (radius 5.0) and two lines.
    # The straight length is 50.0 (from start_uv to end_uv of lines).
    # The overall width (u-direction) = straight_length + 2*radius = 50 + 10 = 60.0
    # The overall height (v-direction) = 2*radius = 10.0

    # We'll create the profile in the XY plane, then extrude in the Z direction.

    # Create the base rectangle for the straight section (50 x 10) centered at origin
    # Then add the semicircular ends.

    # Approach: Use a workplane and build the stadium shape using lines and arcs.

    result = (
        cq.Workplane("XY")
        .center(0, 0)
        .moveTo(0, 5)  # start at top-left of straight section (left arc top)
        .threePointArc((0, 0), (0, -5))  # left arc (radius 5, center at (0,0))
        .lineTo(50, -5)  # bottom line
        .threePointArc((50, 0), (50, 5))  # right arc (radius 5, center at (50,0))
        .lineTo(0, 5)  # top line back to start
        .close()
        .extrude(100.0)  # extrude in +Z direction by 100 mm
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\104453_aba0f2d1_0002\neg_02/generated.step")

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
