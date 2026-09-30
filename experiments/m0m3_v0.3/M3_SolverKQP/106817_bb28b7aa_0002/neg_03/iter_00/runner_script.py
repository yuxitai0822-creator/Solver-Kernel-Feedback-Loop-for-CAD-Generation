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

    # Design Plan: thumb screw (disk)
    # Body: extruded circle
    #   Profile: circle, radius=4.87045 mm, center_uv=(11.430000364780426, 0.0)
    #   Extrude: one_side, direction=+w, distance=6.8707 mm
    # Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    #   => sketch on XZ plane, extrude along Y (positive)

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

    # Parameters from design plan
    radius = 4.87045  # mm
    extrude_distance = 6.8707  # mm
    center_x = 11.430000364780426  # uv coordinate in sketch plane
    center_y = 0.0

    # Build the part
    # Workplane: XZ (since v_dir = (0,0,-1) means sketch normal is -Z? Actually w_dir=(0,1,0) is extrusion direction)
    # Let's use XY plane and then rotate? Simpler: use XZ plane directly.
    # The frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
    # So sketch plane is defined by u and v axes: X and -Z => XZ plane
    # Extrude along w = Y axis

    result = (
        cq.Workplane("XZ")
        .moveTo(center_x, center_y)
        .circle(radius)
        .extrude(extrude_distance)
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
