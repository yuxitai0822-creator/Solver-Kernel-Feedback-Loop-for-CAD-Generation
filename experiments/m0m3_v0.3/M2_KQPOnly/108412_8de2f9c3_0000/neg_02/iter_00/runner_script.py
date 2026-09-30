import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108412_8de2f9c3_0000\neg_02\iter_00\generated.step"

    # Design Plan dimensions (in mm, after cm->mm conversion):
    # Rectangle: length_u = 2438.4 mm, width_v = 1219.2 mm
    # Extrude distance: 12.7 mm
    # The profile coordinates in the design plan are given in UV space:
    #   start_uv = [121.92, -60.96] ... end_uv = [121.92, 60.96] etc.
    # These are in cm originally? Actually the plan says unit_conversion_applied: cm_to_mm (x10)
    # So the UV values are in mm already. But the dimensions say length_u=2438.4, width_v=1219.2.
    # The UV coordinates given span from -121.92 to 121.92 in both axes, which is 243.84 mm.
    # That's 1/10 of the expected 2438.4 mm. So we need to scale the profile by 10x.
    # Alternatively, we can just build the rectangle directly from the dimensions.

    # Build the part using the explicit dimensions from the design plan:
    length_u = 2438.4  # mm
    width_v = 1219.2   # mm
    extrude_dist = 12.7  # mm

    # Create workplane on XY plane
    result = (
        cq.Workplane("XY")
        .rect(length_u, width_v, centered=True)
        .extrude(extrude_dist)
    )

    # Export to STEP
    exporters.export(result, OUT_STEP_PATH)

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
