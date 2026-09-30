import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular prism with dimensions:
    # Length (u): 95.25 mm
    # Width (v): 19.05 mm
    # Height (w): 12.7 mm

    # The design plan specifies a rectangle profile in the uv-plane, extruded along +w.
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # This means: u -> X, v -> -Z, w -> Y.
    # So the rectangle lies in the XZ plane (with v along -Z), and extrudes along Y.

    # Build the rectangle profile on the XZ plane (Y=0).
    # The rectangle spans from (0,0) to (95.25, 19.05) in (u,v) coordinates.
    # In world: u -> X, v -> -Z, so:
    #   start_uv (0, 1.905) -> world (0, 0, -1.905)
    #   end_uv (9.525, 0) -> world (9.525, 0, 0)
    # But the profile curves show a rectangle from (0,0) to (9.525, 1.905) in uv.
    # Note: The dimensions say length_u = 95.25, width_v = 19.05.
    # The uv coordinates in the curves are scaled by 0.1? Actually the curves show
    # start_uv (0, 1.905) to (0,0) etc. The max uv is 9.525 x 1.905.
    # This is a 10x scaling factor from the actual dimensions (95.25/10 = 9.525, 19.05/10 = 1.905).
    # So the profile is defined in a normalized/local uv space scaled by 10.
    # We'll build the rectangle directly with the actual dimensions.

    # Create the rectangle on the XZ plane (Y=0), centered at origin for convenience.
    # The rectangle spans 95.25 mm along X and 19.05 mm along Z.
    # We'll place it so that the min corner is at (0, 0, -19.05) to match the uv frame.
    # Actually, let's just build a simple box with the correct dimensions.

    # Using a box is the simplest approach for a rectangular prism.
    result = cq.Workplane("XY").box(95.25, 12.7, 19.05).translate((95.25/2, 12.7/2, 19.05/2))

    # But we need to match the frame orientation: u=X, v=-Z, w=Y.
    # The box dimensions: length along X = 95.25, height along Y = 12.7, depth along Z = 19.05.
    # This gives the correct spans: X=95.25, Y=12.7, Z=19.05.
    # However, the v direction is -Z, so the span along v is 19.05 (positive magnitude).
    # The box is created with its center at (95.25/2, 12.7/2, 19.05/2) so that the
    # min corner is at (0,0,0) in world coordinates.

    # Export the result
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0006\\ex2/generated.step")

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
