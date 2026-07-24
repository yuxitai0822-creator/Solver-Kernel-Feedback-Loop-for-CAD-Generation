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

    # Create the rectangle on the XY plane (X = u, Y = w? Actually: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0])
    # So u = X, v = -Z, w = Y. The profile is in the uv-plane, which is X-Z plane (with v inverted).
    # We'll just create a rectangle centered at origin and extrude along Y.

    # Dimensions from design plan:
    length_u = 171.45  # along X
    width_v = 38.1     # along Z (but v_dir is [0,0,-1], so we use positive Z and negate? Actually v_dir = [0,0,-1] means v axis points in -Z direction.
    # The profile coordinates: start_uv (0, 3.81) to (0,0) to (17.145, 0) to (17.145, 3.81) back to (0, 3.81)
    # But the dimensions say length_u = 171.45, width_v = 38.1. The profile coordinates seem scaled by 10? 
    # Actually note: compiler notes say "unit_conversion_applied: cm_to_mm (x10)". So the profile coordinates are in cm? 
    # The profile shows 17.145 and 3.81, which multiplied by 10 give 171.45 and 38.1. So the profile is in cm, but we work in mm.
    # So we use the explicit dimensions: 171.45 mm x 38.1 mm, extrude 6.35 mm.

    # Build the plate centered at origin for simplicity, then we can translate if needed.
    # The frame: u_dir = X, v_dir = -Z, w_dir = Y. So the plate lies in the X-Z plane (with v inverted, but that just flips orientation).
    # We'll create a rectangle on the XY plane and then rotate? Actually easier: create on XZ plane.

    # Create workplane on XZ plane (front view in cq)
    result = (cq.Workplane("XZ")
              .rect(length_u, width_v)
              .extrude(6.35))

    # The extrusion direction is normal to the workplane, which for XZ plane is Y direction.
    # w_dir = [0,1,0] so +w = +Y, which matches.

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\108850_0dcd5ef1_0002\neg_03/generated.step")

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
