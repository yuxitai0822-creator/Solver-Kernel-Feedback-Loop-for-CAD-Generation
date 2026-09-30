import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate with dimensions from the design plan
    # The rectangle spans from (-121.92, -60.96) to (121.92, 60.96) in UV space
    # This gives length_u = 243.84 mm and width_v = 121.92 mm
    # Note: The design plan dimensions show length_u=2438.4 and width_v=1219.2, but the UV coordinates
    # are in cm (as noted in compiler_notes: cm_to_mm x10). So UV coords are in cm, multiply by 10 to get mm.
    # Actually, the UV coordinates are already in mm after conversion? Let's check:
    # The design plan says unit is mm, and compiler notes say cm_to_mm (x10).
    # The UV coordinates: 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm
    # So the rectangle spans from (-1219.2, -609.6) to (1219.2, 609.6) in mm
    # That gives length_u = 2438.4 mm, width_v = 1219.2 mm — matching the dimensions.

    # Build the rectangle and extrude
    result = (cq.Workplane("XY")
              .rect(2438.4, 1219.2)
              .extrude(12.7))

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108412_8de2f9c3_0000\neg_01/generated.step")

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
