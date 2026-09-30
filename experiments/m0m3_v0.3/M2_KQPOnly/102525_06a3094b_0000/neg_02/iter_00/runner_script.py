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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0000\neg_02\iter_00\generated.step"

    # Design Plan: rectangular prism with dimensions 3.9mm x 4.9mm x 1.55mm
    # The profile is centered at origin, extruded in +Z direction
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means: u=X, v=-Z, w=Y
    # So the rectangle is in XZ plane (u,v) and extrudes along Y (w)

    # Rectangle dimensions from design plan:
    length_u = 3.9  # along X
    width_v = 4.9   # along Z (but v_dir is [0,0,-1], so width is along Z)
    extrude_distance = 1.55  # along Y

    # Build the part
    # Workplane XZ matches the frame: u=X, v=-Z (cq uses positive Z, so we need to handle sign)
    # The rectangle is centered at origin in the sketch plane
    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .rect(length_u, width_v, centered=True)
        .extrude(extrude_distance)
    )

    # Verify dimensions (optional, but good for debugging)
    # The resulting solid should have bounding box: X: [-1.95, 1.95], Y: [0, 1.55], Z: [-2.45, 2.45]

    # Export to STEP
    exporters.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")
    print(f"Bounding box: {result.val().BoundingBox()}")

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
