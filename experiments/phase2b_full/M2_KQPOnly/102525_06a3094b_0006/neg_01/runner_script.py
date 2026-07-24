import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular prism based on the design plan
    # Dimensions: length_u = 11.3 mm, width_v = 21.0 mm, extrude_distance = 3.0 mm
    # The profile is centered on the origin in the UV plane, then extruded in +W direction

    # Create the rectangle profile centered at origin
    # The profile coordinates from the plan show a rectangle from (-0.565, -1.05) to (0.565, 1.05) in UV space
    # But the actual dimensions are length_u=11.3, width_v=21.0
    # The UV coordinates appear to be half-dimensions: 11.3/2 = 5.65? No, 0.565*10 = 5.65, 1.05*10 = 10.5
    # The plan notes unit_conversion_applied: cm_to_mm (x10), so the UV values are in cm and need scaling
    # Actually, the dimensions are given as 11.3 and 21.0 mm, so we use those directly

    # Create the rectangle profile centered at origin
    result = (cq.Workplane("XY")
              .rect(11.3, 21.0, centered=True)
              .extrude(3.0))

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0006\neg_01/generated.step")

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
