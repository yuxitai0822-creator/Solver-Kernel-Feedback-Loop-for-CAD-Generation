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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0003\neg_02\iter_00/generated.step"

    # Design Plan: extruded circle (disk)
    # Profile: circle, center_uv = (1.6994660913961006, 1.7998556732836484), radius = 2.54
    # Extrude: one_side, +w, distance = 8.89
    # Note: The design plan's profile radius is 2.54, but the perturbation description says radius changed from 2.54 to 3.175.
    # The previous script used radius 31.75 (which is 2.54*12.5? Actually 2.54*12.5=31.75, but that seems wrong).
    # The design plan dimensions section says radius = 25.4 (which is 2.54*10). There is inconsistency.
    # We follow the design plan's profile radius = 2.54 and extrude distance = 8.89.
    # The center_uv in the design plan is (1.6994660913961006, 1.7998556732836484).
    # We'll create a circle at that center with radius 2.54, then extrude 8.89 in +Z.

    result = (
        cq.Workplane("XY")
        .moveTo(1.6994660913961006, 1.7998556732836484)
        .circle(2.54)
        .extrude(8.89)
    )

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
