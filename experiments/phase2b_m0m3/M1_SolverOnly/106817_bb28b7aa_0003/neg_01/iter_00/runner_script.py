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

    # Design Plan parameters
    # Extruded circle (disk) with:
    # - Circle center in UV: (5.080000162124634, 6.350000202655792) but note unit conversion cm->mm
    # - Circle radius: 0.4711700000000002 cm = 4.7117 mm
    # - Extrude distance: 12.192 mm (from design plan, not the perturbed value)
    # - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    #   This means sketch plane is XZ (u=x, v=z), extrude along +w = +y

    # Parameters (all in mm)
    CENTER_X = 5.080000162124634 * 10  # cm to mm
    CENTER_Y = 6.350000202655792 * 10  # cm to mm
    RADIUS = 0.4711700000000002 * 10   # cm to mm = 4.7117 mm
    EXTRUDE_DIST = 12.192  # mm (from design plan, not perturbed)

    # Build the disk
    # Workplane on XZ (since v_dir = [0,0,-1] means z is the sketch vertical)
    # Actually: u_dir=[1,0,0] (x), v_dir=[0,0,-1] (negative z), w_dir=[0,1,0] (y)
    # So sketch plane is XZ, extrude along +Y
    result = (
        cq.Workplane("XZ")
        .moveTo(CENTER_X, CENTER_Y)
        .circle(RADIUS)
        .extrude(EXTRUDE_DIST)
    )

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0003\neg_01\iter_00/generated.step"
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
