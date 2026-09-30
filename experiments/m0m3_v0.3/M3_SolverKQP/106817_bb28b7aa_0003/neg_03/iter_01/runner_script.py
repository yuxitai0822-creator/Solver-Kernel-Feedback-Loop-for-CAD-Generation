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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0003\neg_03\iter_01/generated.step"

    # Design Plan parameters:
    # The design plan specifies a disk (extruded circle) with:
    # - Circle radius = 4.7117 mm (converted from 0.47117 cm)
    # - Extrude distance = 12.192 mm
    # - The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    #   This means: u = X, v = -Z, w = Y
    #   So the circle lies in the X-Z plane (u-v plane) and extrudes along Y (w direction)
    # - Center_uv = (5.080000162124634, 6.350000202655792) in cm -> (50.80000162124634, 63.50000202655792) in mm
    #   These are coordinates in the u-v frame, which maps to X and -Z respectively
    # - Expected spans: u_span = 9.4234 (diameter along X), v_span = 9.4234 (diameter along -Z), w_span = 12.192 (extrude along Y)
    #
    # The previous script used XY plane which caused axis misalignment.
    # We need to use XZ plane so that:
    # - circle lies in XZ plane (u=X, v=-Z)
    # - extrude along Y (w direction)
    # - This gives: bbox X = 9.4234, bbox Z = 9.4234, bbox Y = 12.192

    # Build the part using XZ plane
    result = (
        cq.Workplane("XZ")
        .moveTo(50.80000162124634, -63.50000202655792)  # v maps to -Z, so negate the v coordinate
        .circle(4.7117)
        .extrude(12.192)
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
