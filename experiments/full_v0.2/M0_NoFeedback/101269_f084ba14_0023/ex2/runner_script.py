import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile based on the design plan
    # The profile is defined in the UV plane where:
    #   u_dir = (1,0,0)  -> X axis
    #   v_dir = (0,0,-1) -> -Z axis
    #   w_dir = (0,1,0)  -> Y axis (extrude direction)
    #
    # The rectangle corners in UV coordinates:
    #   (0, 0), (9.525, 0), (9.525, 57.15), (0, 57.15)
    # But note: the design plan dimensions show length_u = 95.25 and width_v = 571.5
    # The UV coordinates in the curves appear to be scaled by 0.1 (likely due to cm->mm conversion)
    # Actually, looking at the dimensions: length_u = 95.25 mm, width_v = 571.5 mm
    # The curves show coordinates up to 9.525 and 57.15, which are 1/10 of the actual dimensions.
    # This is because the source was in cm and converted to mm (x10 factor mentioned in compiler_notes).
    # So the actual rectangle in mm is: width (along u) = 95.25 mm, height (along v) = 571.5 mm

    # Create the rectangle in the XY plane (since u_dir = X, v_dir = -Z, we need to orient properly)
    # Using the frame: u_dir=(1,0,0)=X, v_dir=(0,0,-1)=-Z, w_dir=(0,1,0)=Y
    # So the sketch plane is X-Z (with v along -Z), and extrude along Y

    # Build the rectangle on the XZ plane (normal = Y axis)
    # The rectangle spans from (0,0) to (95.25, 571.5) in the XZ plane
    # But v_dir is (0,0,-1), so the v coordinate maps to -Z
    # So point (u,v) maps to (u, 0, -v) in world coordinates

    # Create the base rectangle
    result = (
        cq.Workplane("XZ")
        .center(95.25/2, -571.5/2)  # center the rectangle so it spans from (0,0) to (95.25, -571.5)
        .rect(95.25, 571.5)
        .extrude(19.05)  # extrude along Y (positive Y = +w direction)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101269_f084ba14_0023\\ex2/generated.step")

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
