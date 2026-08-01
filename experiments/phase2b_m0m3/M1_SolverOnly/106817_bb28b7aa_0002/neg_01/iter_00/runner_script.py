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

    # Design parameters from the design plan
    # The design plan specifies:
    # - Circle center in UV: (11.430000364780426, 0.0) but the profile center_uv is (114.300004, 0.0)
    #   The compiler note says cm_to_mm (x10) was applied, so the original center was 11.43 cm = 114.3 mm
    # - Circle radius: 4.87045 mm (from dimensions.profiles[0].radius)
    # - Extrude distance: 6.8707 mm (from dimensions.extrude_distance)
    # - The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    #   This means the sketch plane is XZ (u=x, v=-z), and extrusion is along w=y

    CENTER_X = 114.300004  # mm
    CENTER_Z = 0.0  # mm (center_uv[1] = 0.0)
    RADIUS = 4.87045  # mm
    EXTRUDE_DISTANCE = 6.8707  # mm

    # Build the model
    # Workplane on XZ plane (since v_dir = [0,0,-1], the sketch plane normal is y)
    # We'll use the XZ workplane which has normal in Y direction
    result = (
        cq.Workplane("XZ")
        .moveTo(CENTER_X, CENTER_Z)
        .circle(RADIUS)
        .extrude(EXTRUDE_DISTANCE)
    )

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0002\neg_01\iter_00/generated.step"
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
