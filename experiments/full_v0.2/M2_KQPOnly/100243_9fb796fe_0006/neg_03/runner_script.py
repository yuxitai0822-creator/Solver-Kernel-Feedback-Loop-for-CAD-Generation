import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: Drone Leg - square strut
    # Profile: rectangle 19mm x 19mm, extruded 130mm
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle is defined in UV plane with corners at:
    #   (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
    # This gives a rectangle of size 1.9 x 1.9 in UV space, but dimensions say 19.0 x 19.0 mm.
    # The UV coordinates appear to be scaled by 10 (cm to mm conversion factor).
    # So we use the explicit dimensions: length_u = 19.0, width_v = 19.0.
    # The rectangle center in UV is at (-57.3282, -12.9901) approximately.
    # We'll construct the rectangle centered at origin in sketch plane, then translate.

    # Build the profile: rectangle 19mm x 19mm
    # The frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # So sketch plane is XZ plane (u along X, v along -Z), extrude along Y (w_dir)

    # Create the rectangle centered at origin in the sketch plane
    profile = cq.Workplane("XZ").rect(19.0, 19.0, centered=True)

    # Extrude along Y (positive Y direction) by 130.0 mm
    result = profile.extrude(130.0)

    # The resulting part is a 19x19x130 mm rectangular strut centered at origin.
    # This matches the design plan dimensions and frame orientation.

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100243_9fb796fe_0006\\neg_03/generated.step")

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
