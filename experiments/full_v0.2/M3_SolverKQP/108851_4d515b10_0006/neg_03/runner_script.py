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

    # The design plan specifies a rectangle in the uv-plane with:
    # u from 0 to 9.524999999999999 (but note: dimensions say length_u = 95.25)
    # v from 0 to 1.905 (but dimensions say width_v = 19.05)
    # The profile coordinates appear to be in cm (divided by 10), so we multiply by 10 to get mm.
    # Actually the compiler notes say "unit_conversion_applied: cm_to_mm (x10)",
    # so the profile values are in cm and need to be scaled by 10 to get mm.

    # Profile rectangle in uv-plane (u, v coordinates):
    # start_uv: (0.0, 1.905) -> (0.0, 19.05) in mm
    # end_uv: (0.0, 0.0) -> (0.0, 0.0) in mm
    # end_uv: (9.524999999999999, 0.0) -> (95.25, 0.0) in mm
    # end_uv: (9.524999999999999, 1.905) -> (95.25, 19.05) in mm
    # back to start: (0.0, 1.905) -> (0.0, 19.05) in mm

    # The extrude direction is +w, where w is along the y-axis (from frame definition).
    # Frame: u_dir = [1,0,0] (x-axis), v_dir = [0,0,-1] (negative z-axis), w_dir = [0,1,0] (y-axis)
    # So the rectangle is in the xz-plane (u=x, v=-z), extruded along y (w).

    # Build the profile in the xz-plane (y=0):
    # Points: (0, 0, -19.05), (0, 0, 0), (95.25, 0, 0), (95.25, 0, -19.05)
    # But v_dir is [0,0,-1], so v=0 maps to z=0, v=1.905 maps to z=-1.905*10 = -19.05

    # Let's build using a simple box approach for clarity:
    # The part is a rectangular prism with dimensions 95.25 x 12.7 x 19.05 (x, y, z)
    # where x = u, y = w (extrude direction), z = -v (since v_dir = [0,0,-1])

    result = cq.Workplane("XY").box(95.25, 12.7, 19.05).translate((95.25/2, 12.7/2, -19.05/2))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0006\\neg_03/generated.step")

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
