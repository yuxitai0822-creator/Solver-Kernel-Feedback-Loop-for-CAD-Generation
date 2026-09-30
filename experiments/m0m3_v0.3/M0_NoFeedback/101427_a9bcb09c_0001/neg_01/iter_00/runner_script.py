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

    # Constants from design plan
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0001\neg_01\iter_00\generated.step"

    # Dimensions (in mm, converted from cm)
    # Outer rectangle: from curves, min x=-2.5, max x=195.5, min y=-2.5, max y=57.5
    # But the design plan says outer_length_u=1980, outer_width_v=600, inner_length_u=1930, inner_width_v=550
    # The curves in the design plan are in UV space, not world coordinates
    # Let's use the explicit dimensions from the design plan

    OUTER_LENGTH = 1980.0  # mm (along u direction)
    OUTER_WIDTH = 600.0    # mm (along v direction)
    INNER_LENGTH = 1930.0  # mm
    INNER_WIDTH = 550.0    # mm
    EXTRUDE_DEPTH = 25.0   # mm (from design plan, not the perturbed 37.5)

    # Build the frame
    result = (
        cq.Workplane("XZ")
        .rect(OUTER_LENGTH, OUTER_WIDTH, centered=True)
        .extrude(EXTRUDE_DEPTH)
    )

    # Cut inner hole
    inner = (
        cq.Workplane("XZ")
        .rect(INNER_LENGTH, INNER_WIDTH, centered=True)
        .extrude(EXTRUDE_DEPTH * 1.5)  # overshoot to ensure clean cut
    )

    result = result.cut(inner)

    # Export
    import os
    os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
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
