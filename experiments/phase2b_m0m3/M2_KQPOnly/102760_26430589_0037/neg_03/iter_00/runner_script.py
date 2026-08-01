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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102760_26430589_0037\neg_03\iter_00\generated.step"

    # Design Plan parameters:
    # - Disk (extruded circle) with radius 0.8 mm, extrude distance 4.0 mm
    # - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # - Extrude direction: -w (i.e., along negative Y axis)
    # - No inner holes (the design plan has only one outer circle, no inner loops)

    # Build the part:
    # 1. Create a workplane on the XZ plane (since v_dir is [0,0,-1] which is Z, and w_dir is [0,1,0] which is Y)
    #    Actually, the frame has u=X, v=-Z, w=Y. So the sketch plane is the X-Z plane (normal = Y).
    #    We'll use Workplane("XZ") which has normal (0,1,0).
    # 2. Draw a circle of radius 0.8 mm centered at (0,0)
    # 3. Extrude in the -w direction (negative Y) by 4.0 mm

    result = (
        cq.Workplane("XZ")
        .circle(0.8)
        .extrude(4.0)  # extrude in +Y by default; we want -Y, but we can just extrude and then mirror or use negative
    )

    # The design plan says extrude direction is -w (negative Y).
    # Since Workplane("XZ").extrude(4.0) extrudes in +Y, we need to flip.
    # We can achieve this by extruding -4.0 or by mirroring.
    # Let's use a negative distance to extrude in -Y direction.
    result = (
        cq.Workplane("XZ")
        .circle(0.8)
        .extrude(-4.0)  # extrude in -Y direction
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
