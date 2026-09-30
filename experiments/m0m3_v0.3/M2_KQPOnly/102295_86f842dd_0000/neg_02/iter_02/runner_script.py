import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_02\iter_02/generated.step"

    # Design Plan: stadium extrusion
    # Stadium profile: two arcs (radius=10.0) connected by two lines (straight_length=28.0)
    # The profile lies in the XZ plane (u=x, v=z), extrude along Y (w direction)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # So sketch plane is XZ, extrude along +Y

    # Stadium dimensions from design plan:
    # radius = 10.0 mm (explicit)
    # straight_length = 28.0 mm (inferred from point span)
    # Extrude distance = 4.0 mm along +Y

    # Build the stadium profile in the XZ plane
    # Center the stadium at origin for simplicity
    # The stadium consists of:
    # - Left arc: center at (-14.0, 0, 0), radius 10.0, from 90° to 270° (or 0 to 180 in local UV)
    # - Top line: from (-14.0, 0, 10.0) to (14.0, 0, 10.0)
    # - Right arc: center at (14.0, 0, 0), radius 10.0, from 270° to 90° (or 0 to 180 in local UV)
    # - Bottom line: from (14.0, 0, -10.0) to (-14.0, 0, -10.0)

    # Using cadquery's Workplane on XZ plane
    # The threePointArc method takes three points: start, middle, end
    # For the left arc: start=(-14,10), middle=(-14,20), end=(14,10) is WRONG because the arc center is at (-14,0)
    # The correct three points for the left arc: start=(-14,10), middle=(-24,0), end=(-14,-10)
    # But we need to traverse the profile in a continuous loop.
    # Let's start at the top-left corner (-14,10), go along the top line to (14,10),
    # then the right arc from (14,10) to (14,-10) with center at (14,0),
    # then the bottom line from (14,-10) to (-14,-10),
    # then the left arc from (-14,-10) to (-14,10) with center at (-14,0).

    result = (
        cq.Workplane("XZ")
        .moveTo(-14.0, 10.0)  # Start at top-left junction
        .lineTo(14.0, 10.0)  # Top line
        .threePointArc((24.0, 0.0), (14.0, -10.0))  # Right arc: start=(14,10), middle=(24,0), end=(14,-10)
        .lineTo(-14.0, -10.0)  # Bottom line
        .threePointArc((-24.0, 0.0), (-14.0, 10.0))  # Left arc: start=(-14,-10), middle=(-24,0), end=(-14,10)
        .close()
        .extrude(4.0)  # Extrude along Y (positive direction)
    )

    # Export to STEP
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
