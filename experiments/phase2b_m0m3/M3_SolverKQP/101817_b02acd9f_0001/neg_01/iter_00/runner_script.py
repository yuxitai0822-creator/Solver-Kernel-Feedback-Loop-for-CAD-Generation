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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0001\neg_01\iter_00/generated.step"

    # Design Plan: extruded rectangular frame
    # Outer rectangle: from (-4.0, 4.0) to (0.0, 0.0) in UV space, but the design plan uses
    # a coordinate system where the outer rectangle spans 40mm x 40mm (outer_length_u=40, outer_width_v=40)
    # and inner rectangle spans 37.6mm x 37.6mm (inner_length_u=37.6, inner_width_v=37.6)
    # The UV coordinates in the design plan are: outer from (-4.0, 4.0) to (0.0, 0.0) which is 4 units x 4 units
    # and inner from (-0.12, 3.88) to (-3.88, 0.12) which is 3.76 units x 3.76 units
    # Since the dimensions are given as 40mm and 37.6mm, the UV coordinates are in cm (x10 factor)
    # So we scale by 10 to get mm: outer 40x40, inner 37.6x37.6
    # Extrude distance: 520.0 mm (from design plan, not the perturbed 780)

    # Build the outer rectangle centered at origin
    outer_w = 40.0
    outer_h = 40.0
    inner_w = 37.6
    inner_h = 37.6
    extrude_dist = 520.0

    # Create workplane and draw outer rectangle
    result = (cq.Workplane("XY")
        .rect(outer_w, outer_h, centered=True)
        .extrude(extrude_dist))

    # Cut inner hole
    inner = (cq.Workplane("XY")
        .rect(inner_w, inner_h, centered=True)
        .extrude(extrude_dist))

    result = result.cut(inner)

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
