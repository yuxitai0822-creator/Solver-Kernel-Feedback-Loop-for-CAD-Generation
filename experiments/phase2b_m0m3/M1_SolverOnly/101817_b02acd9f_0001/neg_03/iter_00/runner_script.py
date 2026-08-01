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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0001\neg_03\iter_00\generated.step"

    # Design Plan: horizontal leg 1
    # Extruded rectangular frame, outer 40x40 mm, inner 37.6x37.6 mm, extrude 520 mm
    # The profile is defined in UV coordinates where:
    #   u_dir = [1,0,0], v_dir = [0,1,0], w_dir = [0,0,1]
    # Outer ring: rectangle from (-4,4) to (0,4) to (0,0) to (-4,0) - this is a 4x4 square
    # Inner ring: rectangle from (-0.12, 3.88) to (-0.12, 0.12) to (-3.88, 0.12) to (-3.88, 3.88)
    # Note: The UV coordinates are in cm (unit conversion cm->mm x10), so multiply by 10

    # Scale factor: cm to mm
    scale = 10.0

    # Outer rectangle dimensions in mm (after scaling)
    outer_w = 4.0 * scale  # 40 mm
    outer_h = 4.0 * scale  # 40 mm

    # Inner rectangle dimensions in mm (after scaling)
    inner_w = (3.88 - 0.12) * scale  # 37.6 mm
    inner_h = (3.88 - 0.12) * scale  # 37.6 mm

    # Center of outer rectangle in UV space: (-2, 2) in cm -> (-20, 20) in mm
    # But we'll construct from the origin for simplicity

    # Build the profile on XY plane
    result = (
        cq.Workplane("XY")
        .rect(outer_w, outer_h, centered=True)
        .extrude(520.0)
    )

    # Cut the inner hole
    inner = (
        cq.Workplane("XY")
        .rect(inner_w, inner_h, centered=True)
        .extrude(520.0)
    )

    result = result.cut(inner)

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
