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

    # Constants from design plan (unit: mm)
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0001\neg_02\iter_00/generated.step"

    # Frame dimensions (from design plan, converted to mm)
    # Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
    # Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
    # Extrude distance: 25.0 mm in +w direction (which is +Y in our coordinate system)

    # The design plan specifies:
    # u_dir = [1,0,0] (X axis)
    # v_dir = [0,0,-1] (negative Z axis)
    # w_dir = [0,1,0] (Y axis)
    # So the profile is in the XZ plane, extruded in Y direction

    # Outer rectangle corners in UV space (u,v):
    # (-2.5, -2.5) -> (-2.5, 57.5) -> (195.5, 57.5) -> (195.5, -2.5)
    # Map to XZ: u->X, v->Z (but v_dir is [0,0,-1], so v maps to -Z)
    # Actually, let's just work in the sketch plane directly.

    # The profile is a rectangular frame in the XZ plane (Y=0)
    # Outer: width=198.0 (from -2.5 to 195.5), height=60.0 (from -2.5 to 57.5)
    # Inner: width=193.0 (from 0.0 to 193.0), height=55.0 (from 0.0 to 55.0)
    # Extrude 25.0 mm in +Y direction

    # Build the frame
    result = (
        cq.Workplane("XZ")
        .rect(198.0, 60.0, centered=False)
        .extrude(25.0)
    )

    # Cut the inner hole
    inner = (
        cq.Workplane("XZ")
        .rect(193.0, 55.0, centered=False)
        .extrude(25.0)
    )

    result = result.cut(inner)

    # Export
    cq.exporters.export(result, OUT_STEP_PATH)

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
