import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile based on the design plan
    # The profile is a rectangle with dimensions 19.0 x 19.0 mm
    # The rectangle is defined in UV space with the given corner coordinates
    # The extrude direction is +w (which maps to +Y in world coordinates)
    # The extrude distance is 130.0 mm

    # Define the rectangle profile points in UV space
    # From the design plan, the rectangle corners are:
    # (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
    # Width in U direction: 2.0 mm (but actual dimension should be 19.0 mm)
    # Height in V direction: 2.0 mm (but actual dimension should be 19.0 mm)
    # The coordinates seem to be offset, so we'll create a centered rectangle of 19x19

    # Create the rectangle centered at origin in the XY plane
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # So we sketch on the XZ plane (since v_dir is -Z, w_dir is Y)
    # Actually, let's use the standard approach: create a rectangle on the XY plane and extrude in Z
    # Then rotate/translate as needed

    # Based on the frame: u_dir = X, v_dir = -Z, w_dir = Y
    # So the profile is in the X-Z plane, and extrusion is along Y

    # Create the rectangle on the XZ plane (using workplane XZ)
    result = (
        cq.Workplane("XZ")
        .rect(19.0, 19.0, centered=True)
        .extrude(130.0)
    )

    # The extrusion direction is +w which is +Y, so the result is correct
    # The rectangle is centered at origin, spanning from -9.5 to 9.5 in X and Z
    # and from 0 to 130 in Y

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\100243_9fb796fe_0006\\neg_01/generated.step")

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
