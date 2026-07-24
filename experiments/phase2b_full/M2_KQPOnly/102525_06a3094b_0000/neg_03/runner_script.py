import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular prism based on the design plan
    # Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
    # The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means: u -> X, v -> -Z, w -> Y
    # So the rectangle is in the X-Z plane (u along X, v along -Z) and extrudes along Y (w direction)

    # Create the rectangle profile in the X-Z plane
    # The profile vertices in uv coordinates:
    # (0.195, -0.245) -> (0.195, 0.245) -> (-0.195, 0.245) -> (-0.195, -0.245)
    # These are centered around (0,0) with half-lengths 0.195 and 0.245
    # But the total dimensions should be 3.9 x 4.9, so half-lengths are 1.95 and 2.45
    # The uv coordinates in the plan appear to be scaled by 0.1 (cm to mm conversion factor of 10)
    # Actually: 0.195 * 10 = 1.95, 0.245 * 10 = 2.45, so the rectangle is 3.9 x 4.9

    # Build the rectangle centered at origin in the X-Z plane
    # u_dir = X axis, v_dir = -Z axis, so v goes in negative Z direction
    # The rectangle spans from -1.95 to 1.95 in X, and from -2.45 to 2.45 in Z (but v_dir is -Z)
    # In uv: u from -0.195 to 0.195, v from -0.245 to 0.245
    # After scaling: u from -1.95 to 1.95, v from -2.45 to 2.45
    # Since v_dir = [0,0,-1], v maps to -Z, so v=-2.45 -> Z=2.45, v=2.45 -> Z=-2.45

    # Create the rectangle using workplane
    result = (cq.Workplane("XY")
              .center(0, 0)
              .rect(3.9, 4.9)
              .extrude(1.55))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0000\\neg_03/generated.step")

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
