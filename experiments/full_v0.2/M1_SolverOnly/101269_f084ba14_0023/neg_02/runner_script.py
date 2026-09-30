import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # The profile is a rectangle with length_u = 95.25 mm and width_v = 571.5 mm
    # Extrude distance = 19.05 mm in the +w direction

    # Create the rectangle profile on the XY plane (u=x, v=y, w=z)
    # The rectangle spans from (0,0) to (95.25, 571.5) in the UV coordinate system
    # Note: The design plan uses a frame where u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # This means: u -> x, v -> -z, w -> y
    # So the rectangle in world coordinates: x from 0 to 95.25, z from -571.5 to 0, extruded in y direction

    # Create the rectangle on the XZ plane (since v_dir is -z)
    # The rectangle corners: (0, 0, -571.5) to (95.25, 0, 0) in (x, y, z)
    # But we'll work in the XY plane and then rotate

    # Simpler approach: create the rectangle in XY plane and extrude in Z, then rotate
    # Rectangle: width=95.25 (x), height=571.5 (y), extrude 19.05 in z

    result = (
        cq.Workplane("XY")
        .rect(95.25, 571.5)
        .extrude(19.05)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101269_f084ba14_0023\\neg_02/generated.step")

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
