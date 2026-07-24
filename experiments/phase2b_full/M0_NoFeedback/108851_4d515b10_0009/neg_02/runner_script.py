import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate based on the design plan
    # The profile is a rectangle with dimensions:
    #   length_u = 209.55 mm (along x-axis)
    #   width_v = 57.912 mm (along z-axis, since v_dir = [0,0,-1])
    # Extrude distance = 19.05 mm along w_dir = [0,1,0] (y-axis)

    # Create the rectangle in the XY plane (we'll work in the local frame)
    # The profile coordinates from the plan:
    #   start_uv = (0.0, 5.7912) -> (0, 5.7912)
    #   end_uv = (0.0, 0.0) -> (0, 0)
    #   end_uv = (20.955, 0.0) -> (20.955, 0)
    #   end_uv = (20.955, 5.7912) -> (20.955, 5.7912)
    # Note: The plan dimensions are length_u=209.55, width_v=57.912
    # The profile coordinates appear to be in cm (divided by 10) because
    # the compiler notes say "cm_to_mm (x10)". So we multiply by 10.
    # Actually, the plan says unit is mm, but the profile values are small.
    # Let's use the explicit dimensions from the plan: 209.55 x 57.912 mm

    # The frame: u_dir = [1,0,0] (x), v_dir = [0,0,-1] (negative z), w_dir = [0,1,0] (y)
    # So the rectangle lies in the XZ plane (u along x, v along z)
    # Extrude along y (w direction)

    # Build the rectangle in the XZ plane
    result = (
        cq.Workplane("XZ")
        .rect(209.55, 57.912)
        .extrude(19.05)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0009\\neg_02/generated.step")

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
