import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: rectangular prism (SOIC-8 body)
    # Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle is centered at origin in uv plane, with half-dimensions:
    #   half_u = 3.9/2 = 1.95, half_v = 4.9/2 = 2.45
    # But the profile curves show start_uv and end_uv values of ±0.195 and ±0.245,
    # which are 1/10 of the actual dimensions (due to cm->mm conversion factor 10).
    # We use the explicit dimensions: 3.9 x 4.9 mm rectangle, extruded 1.55 mm in +w direction.

    # Build the rectangle in the uv-plane (u = x, v = z, w = y)
    # The rectangle is centered at (0,0) in uv, with u extent = 3.9, v extent = 4.9
    result = (
        cq.Workplane("XY")
        .rect(3.9, 4.9, centered=True)
        .extrude(1.55)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102525_06a3094b_0000\neg_01/generated.step")

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
