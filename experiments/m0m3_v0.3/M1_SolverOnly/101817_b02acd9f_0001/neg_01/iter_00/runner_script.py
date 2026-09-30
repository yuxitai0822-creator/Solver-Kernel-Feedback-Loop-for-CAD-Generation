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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0001\neg_01\iter_00/generated.step"

    # Design Plan dimensions (in mm, after cm->mm conversion x10):
    # Outer rectangle: 40 x 40 mm (from -4.0 to 0.0 in u, 0.0 to 4.0 in v, scaled by 10)
    # Inner rectangle: 37.6 x 37.6 mm (from -3.88 to -0.12 in u, 0.12 to 3.88 in v, scaled by 10)
    # Extrude distance: 520.0 mm (original 52.0 cm * 10)

    # The design plan specifies:
    # - Outer ring: points at (-4,4), (0,4), (0,0), (-4,0) in uv coordinates
    # - Inner ring: points at (-0.12, 3.88), (-0.12, 0.12), (-3.88, 0.12), (-3.88, 3.88)
    # - Extrude: 520.0 mm in +w direction

    # Scale factor from design plan uv to mm: multiply by 10 (since dimensions are 40mm and 37.6mm)
    scale = 10.0

    # Outer rectangle corners (in mm)
    outer_pts = [
        (-4.0 * scale, 4.0 * scale),   # (-40, 40)
        (0.0 * scale, 4.0 * scale),    # (0, 40)
        (0.0 * scale, 0.0 * scale),    # (0, 0)
        (-4.0 * scale, 0.0 * scale)    # (-40, 0)
    ]

    # Inner rectangle corners (in mm)
    inner_pts = [
        (-0.12 * scale, 3.88 * scale),   # (-1.2, 38.8)
        (-0.12 * scale, 0.12 * scale),   # (-1.2, 1.2)
        (-3.88 * scale, 0.12 * scale),   # (-38.8, 1.2)
        (-3.88 * scale, 3.88 * scale)    # (-38.8, 38.8)
    ]

    extrude_distance = 520.0  # mm

    # Build the part
    result = (
        cq.Workplane("XY")
        .moveTo(outer_pts[0][0], outer_pts[0][1])
        .lineTo(outer_pts[1][0], outer_pts[1][1])
        .lineTo(outer_pts[2][0], outer_pts[2][1])
        .lineTo(outer_pts[3][0], outer_pts[3][1])
        .close()
        .extrude(extrude_distance)
    )

    # Cut the inner hole
    inner_wire = (
        cq.Workplane("XY")
        .moveTo(inner_pts[0][0], inner_pts[0][1])
        .lineTo(inner_pts[1][0], inner_pts[1][1])
        .lineTo(inner_pts[2][0], inner_pts[2][1])
        .lineTo(inner_pts[3][0], inner_pts[3][1])
        .close()
        .extrude(extrude_distance * 1.5)  # overshoot to ensure clean cut
    )

    result = result.cut(inner_wire)

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
