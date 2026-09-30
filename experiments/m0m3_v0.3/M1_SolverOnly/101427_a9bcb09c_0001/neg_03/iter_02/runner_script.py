import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    from cadquery import exporters

    # Design Plan: extruded rectangular frame (hollow box)
    # Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5 (in UV frame)
    # Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    # Extrude in +w direction by 25.0 mm
    # UV frame: u = x, v = -z, w = y (per design plan frame axes)
    # So we work on XZ plane, extrude in Y direction

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0001\neg_03\iter_02/generated.step"

    # Build the outer rectangle on XZ plane
    # Outer: u from -2.5 to 195.5, v from -2.5 to 57.5
    # In XZ: x = u, z = -v (since v_dir = [0,0,-1])
    # So outer: x from -2.5 to 195.5, z from -57.5 to 2.5
    outer_xmin, outer_xmax = -2.5, 195.5
    outer_zmin, outer_zmax = -57.5, 2.5
    outer_w = outer_xmax - outer_xmin  # 198.0
    outer_h = outer_zmax - outer_zmin  # 60.0
    outer_cx = (outer_xmin + outer_xmax) / 2  # 96.5
    outer_cz = (outer_zmin + outer_zmax) / 2  # -27.5

    # Inner: u from 0.0 to 193.0, v from 0.0 to 55.0
    # In XZ: x from 0.0 to 193.0, z from -55.0 to 0.0
    inner_xmin, inner_xmax = 0.0, 193.0
    inner_zmin, inner_zmax = -55.0, 0.0
    inner_w = inner_xmax - inner_xmin  # 193.0
    inner_h = inner_zmax - inner_zmin  # 55.0
    inner_cx = (inner_xmin + inner_xmax) / 2  # 96.5
    inner_cz = (inner_zmin + inner_zmax) / 2  # -27.5

    # Build the frame
    result = (
        cq.Workplane("XZ")
        .moveTo(outer_cx, outer_cz)
        .rect(outer_w, outer_h, centered=True)
        .extrude(25.0)  # extrude in +Y (which is +w direction)
    )

    # Cut inner hole
    inner_cutter = (
        cq.Workplane("XZ")
        .moveTo(inner_cx, inner_cz)
        .rect(inner_w, inner_h, centered=True)
        .extrude(25.0 * 1.5)  # overshoot to ensure clean cut
    )

    result = result.cut(inner_cutter)

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
