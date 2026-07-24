import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # The profile is a rectangle of size 171.45 mm x 38.1 mm (length_u x width_v)
    # Extrude by 6.35 mm in the +w direction (which corresponds to +y in world coordinates)

    # Create the rectangle on the XY plane (X = u, Y = w? Actually we need to map correctly)
    # From the design plan: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # So u = X, v = -Z, w = Y
    # The rectangle is defined in UV space: u from 0 to 171.45, v from 0 to 38.1
    # But the curves show v from 0 to 3.81? Wait, the curves show start_uv and end_uv values
    # that are 10x smaller. The dimensions say length_u=171.45, width_v=38.1.
    # The curves show values like 0, 3.81, 17.145 which are 1/10 of the actual dimensions.
    # This is because the source was in cm and converted to mm (x10).
    # So the actual rectangle is 171.45 mm x 38.1 mm.

    # Build the plate
    result = (
        cq.Workplane("XY")
        .rect(171.45, 38.1)
        .extrude(6.35)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\108850_0dcd5ef1_0002\neg_01/generated.step")

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
