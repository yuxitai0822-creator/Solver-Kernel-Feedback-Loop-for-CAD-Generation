import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # The profile is a rectangle in the UV plane, then extruded in the W direction
    # From the design plan:
    #   - length_u = 95.25 mm (along X axis)
    #   - width_v = 571.5 mm (along Z axis, since v_dir = [0,0,-1])
    #   - extrude distance = 19.05 mm (along Y axis, since w_dir = [0,1,0])
    # The profile coordinates in UV space:
    #   start_uv = (9.525, 57.15)  -> this is the top-right corner
    #   end_uv = (9.525, 0.0)      -> bottom-right
    #   start_uv = (0.0, 57.15)    -> top-left
    #   end_uv = (0.0, 0.0)        -> bottom-left
    # So the rectangle spans from u=0 to u=9.525 and v=0 to v=57.15
    # But the dimensions say length_u=95.25 and width_v=571.5
    # The UV coordinates appear to be scaled by 10 (since compiler notes say cm_to_mm x10)
    # Actually 9.525*10 = 95.25 and 57.15*10 = 571.5, so the UV values are in cm
    # We'll use the explicit dimensions directly: 95.25 x 571.5 mm

    # Build the rectangle centered at origin for simplicity, then extrude
    result = (
        cq.Workplane("XY")
        .rect(95.25, 571.5)
        .extrude(19.05)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\neg_01/generated.step")

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
