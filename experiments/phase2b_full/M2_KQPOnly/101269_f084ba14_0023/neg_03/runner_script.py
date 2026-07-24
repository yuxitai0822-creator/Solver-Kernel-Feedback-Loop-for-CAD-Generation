import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular profile in the XY plane
    # The design plan specifies a rectangle with dimensions:
    #   length_u = 95.25 mm (along x-axis)
    #   width_v = 571.5 mm (along y-axis, but note v_dir is [0,0,-1] so we use negative y)
    # The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # This means: u -> x, v -> -z, w -> y
    # The profile is defined in uv space, with points:
    #   (9.525, 57.15), (9.525, 0), (0, 57.15), (0, 0)
    # These are offsets from the origin in the uv coordinate system.
    # Since the rectangle spans from u=0 to u=9.525 and v=0 to v=57.15,
    # but the actual dimensions are length_u=95.25 and width_v=571.5,
    # the uv coordinates are scaled by a factor of 10.
    # So we create a rectangle from (0,0) to (95.25, 571.5) in the uv plane.
    # In the frame: u -> x, v -> -z, so the rectangle lies in the xz plane.
    # We'll create the rectangle in the XY plane and then rotate if needed.
    # Simpler: create a rectangle in the XY plane with dimensions 95.25 x 571.5
    # and extrude along Z by 19.05 mm.

    # Create the base rectangle
    result = (
        cq.Workplane("XY")
        .rect(95.25, 571.5)
        .extrude(19.05)
    )

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\neg_03/generated.step")

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
