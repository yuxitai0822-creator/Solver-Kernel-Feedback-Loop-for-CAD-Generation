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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_02\iter_00\generated.step"

    # Design Plan parameters:
    # - Disk with radius 0.8 mm (from dimensions.profiles[0].radius.value)
    # - Extrude distance 4.0 mm (from dimensions.extrude_distance.value)
    # - Circle profile radius 0.08 mm (from profiles[0].rings[0].curves[0].radius) - this is the sketch radius
    # - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # - Extrude direction: -w (i.e., along negative Y axis)

    # Build the part:
    # 1. Create a circle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
    # 2. Extrude along Y direction (w_dir is [0,1,0], extrude in -w = negative Y)

    # The circle radius in the sketch is 0.08 mm (from the curves section)
    # But the actual part radius is 0.8 mm (from dimensions section)
    # The perturbation changed the sketch radius from 0.08 to 0.1
    # We use the perturbed value: 0.1 mm for the sketch circle
    # The extrude distance is 4.0 mm

    # Create workplane on XZ plane
    result = (
        cq.Workplane("XZ")
        .circle(0.1)  # perturbed radius from 0.08 to 0.1
        .extrude(4.0)  # extrude along Y (positive Y since we're on XZ plane)
    )

    # The extrude direction should be -w = negative Y
    # Since we're on XZ plane, extrude goes in +Y by default
    # To extrude in -Y, we need to negate the distance
    # But the design says direction is -w, so we extrude in negative Y
    # Rebuild with correct direction
    result = (
        cq.Workplane("XZ")
        .circle(0.1)  # perturbed radius
        .extrude(-4.0)  # extrude in negative Y direction
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
