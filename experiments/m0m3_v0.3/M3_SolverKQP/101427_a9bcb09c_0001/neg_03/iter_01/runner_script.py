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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0001\neg_03\iter_01/generated.step"

    # Design Plan: rectangular frame with outer dimensions ~1980mm x 600mm, inner ~1930mm x 550mm, extruded 25mm
    # The perturbation (E4_void_remove) removes the inner void, so we produce a solid rectangular plate.
    # However, the kernel feedback indicates through_void_count expected 1, so we must restore the inner void.

    # Outer rectangle dimensions (from design plan curves, scaled by 10 from cm to mm)
    outer_xmin = -2.5 * 10  # -25
    outer_xmax = 195.5 * 10  # 1955
    outer_ymin = -2.5 * 10   # -25
    outer_ymax = 57.5 * 10   # 575

    # Inner rectangle dimensions (from design plan curves, scaled by 10)
    inner_xmin = 0.0 * 10    # 0
    inner_xmax = 193.0 * 10  # 1930
    inner_ymin = 0.0 * 10    # 0
    inner_ymax = 55.0 * 10   # 550

    # Extrude distance (25mm)
    extrude_dist = 25.0

    # Build the outer rectangle
    result = (
        cq.Workplane("XZ")
        .center((outer_xmin + outer_xmax) / 2, (outer_ymin + outer_ymax) / 2)
        .rect(outer_xmax - outer_xmin, outer_ymax - outer_ymin)
        .extrude(extrude_dist)
    )

    # Cut the inner rectangle to create the void (restoring the through hole)
    result = (
        result.faces(">Z").workplane()
        .center((inner_xmin + inner_xmax) / 2, (inner_ymin + inner_ymax) / 2)
        .rect(inner_xmax - inner_xmin, inner_ymax - inner_ymin)
        .cutThruAll()
    )

    # Export
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
