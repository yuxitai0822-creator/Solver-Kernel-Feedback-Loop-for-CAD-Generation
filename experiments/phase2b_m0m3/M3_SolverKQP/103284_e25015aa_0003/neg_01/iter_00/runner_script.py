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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0003\neg_01\iter_00/generated.step"

    # Design Plan parameters (from solid_bodies[0])
    # Profile: circle, center_uv = [1.6994660913961006, 1.7998556732836484], radius = 2.54
    # Extrude: one_side, +w, distance_total = 8.89
    # Dimensions: radius = 25.4, center_uv = [16.994661, 17.998557]
    # Note: The profile center_uv and radius appear to be in a different scale than dimensions.
    # The dimensions section says radius=25.4, center_uv=[16.994661, 17.998557].
    # The profile section says radius=2.54, center_uv=[1.6994660913961006, 1.7998556732836484].
    # The compiler notes say unit_conversion_applied: cm_to_mm (x10).
    # The profile values are likely in cm (since 2.54 cm = 25.4 mm, 1.699... cm ≈ 16.99 mm).
    # So we use the dimension values (in mm): radius=25.4, center=(16.994661, 17.998557), extrude=8.89.

    # Build the part
    result = (
        cq.Workplane("XY")
        .moveTo(16.994661, 17.998557)
        .circle(25.4)
        .extrude(8.89)
    )

    # Export STEP
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
