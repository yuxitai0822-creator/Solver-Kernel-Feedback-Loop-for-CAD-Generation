import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Lever Switch - Disk
    # Dimensions:
    #   Radius: 25.4 mm (from dimensions.profiles[0].radius.value)
    #   Extrude distance: 8.89 mm (from dimensions.extrude_distance.value)
    #   Center UV: (16.994661, 17.998557) - used for positioning in sketch plane
    #   Profile circle center_uv: (1.6994660913961006, 1.7998556732836484) - this is the actual circle center in sketch
    #   Note: The profile circle radius is 2.54 (from curves), but dimensions say 25.4.
    #   The dimensions section overrides the curve radius: radius = 25.4 mm.
    #   The center_uv in dimensions is (16.994661, 17.998557) which is ~10x the curve center.
    #   This suggests the sketch is in a local coordinate system scaled by 10 (cm to mm conversion).
    #   We'll use the dimension values directly: radius 25.4, center at (16.994661, 17.998557).
    #   Extrude in +w direction (z-axis) by 8.89 mm.

    radius = 25.4
    center_x = 16.994661
    center_y = 17.998557
    height = 8.89

    # Build the disk: circle at (center_x, center_y) extruded upward
    result = (
        cq.Workplane("XY")
        .center(center_x, center_y)
        .circle(radius)
        .extrude(height)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\103284_e25015aa_0003\neg_02/generated.step")

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
