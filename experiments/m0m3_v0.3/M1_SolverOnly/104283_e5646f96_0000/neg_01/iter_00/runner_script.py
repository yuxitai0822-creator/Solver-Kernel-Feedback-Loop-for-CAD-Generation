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

    # Design Plan: SHAFT[ v1
    # Extruded circle (disk) with radius 12.5 mm, extrude distance 75.0 mm
    # Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
    # Circle center in UV: (-15.0, 10.0) -> but in the frame, this is a local coordinate
    # The frame indicates the sketch plane is YZ (since w_dir is X axis)
    # So we work on YZ plane, center at (-15.0, 10.0) in YZ coordinates

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0000\neg_01\iter_00\generated.step"

    # Build on YZ plane (since w_dir = [1,0,0] means extrusion along X)
    # The circle center in UV coordinates is (-15.0, 10.0)
    # In YZ plane: U corresponds to -Z? Actually u_dir=[0,0,-1], v_dir=[0,1,0]
    # So U axis = -Z, V axis = Y
    # Center in YZ: Y = v_coord = 10.0, Z = -u_coord = -(-15.0) = 15.0
    # But simpler: just use the UV coordinates directly on a workplane

    # Create workplane on YZ
    wp = cq.Workplane("YZ")

    # Move to center and create circle with radius 12.5 mm
    # The center in UV is (-15.0, 10.0). In YZ plane, we use (y, z) = (10.0, 15.0)
    # because u_dir = [0,0,-1] means u maps to -z, so u=-15 gives z=15
    result = wp.moveTo(10.0, 15.0).circle(12.5).extrude(75.0)

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
