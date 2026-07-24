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
    #   length_u = 307.848 mm (along x-axis)
    #   width_v = 19.05 mm (along z-axis, since v_dir = [0,0,-1])
    # Extrude distance = 12.7 mm (along y-axis, since w_dir = [0,1,0])

    # Create the rectangle profile on the XY plane (z=0)
    # The profile coordinates in UV space:
    #   start at (0, 1.905) -> (0, 0) -> (30.7848, 0) -> (30.7848, 1.905) -> back to start
    # Note: The UV coordinates are scaled: U ranges 0 to 30.7848, V ranges 0 to 1.905
    # But the actual dimensions are length_u=307.848 and width_v=19.05
    # The UV coordinates appear to be in cm (since compiler notes say cm_to_mm x10)
    # So we need to multiply by 10 to get mm: 30.7848*10 = 307.848, 1.905*10 = 19.05

    # Build the plate using a rectangle centered at origin for simplicity
    # The plate spans: x from -153.924 to 153.924, z from -9.525 to 9.525
    # Extrude along y-axis by 12.7 mm

    result = (
        cq.Workplane("XY")
        .rect(307.848, 19.05)  # width along x, height along z
        .extrude(12.7)  # extrude along y (positive direction)
    )

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\108851_4d515b10_0005\ex2/generated.step")

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
