import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq
    import math

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0006\neg_03\iter_00/generated.step"

    # Design Plan: Drone Leg - square strut
    # Profile: rectangle 19mm x 19mm (in UV plane)
    # Extrude: 130mm along W direction
    # Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
    # The rectangle center is at UV origin, with half-widths 9.5mm

    # Build on XY plane, then rotate to match frame orientation
    # Frame: U=X, V=-Z, W=Y
    # So we sketch on XZ plane (since V is -Z, but we can just use XY and rotate)
    # Actually simpler: sketch on XY plane, extrude along Y, then rotate if needed
    # But the frame says W=Y, so extrude along Y is correct.
    # The rectangle is in UV plane: U=X, V=-Z. So on XY plane, we need to map:
    #   U -> X, V -> -Z. So we sketch on XY plane with width along X and height along Y?
    # No: V is -Z, so the rectangle lies in XZ plane. Let's use Workplane("XZ").

    # Rectangle center at (0,0) in UV, which maps to (0,0) in XZ.
    # Rectangle dimensions: length_u=19mm along X, width_v=19mm along Z (but V=-Z, so width along -Z)
    # Since centered, it's symmetric.

    result = (
        cq.Workplane("XZ")
        .center(0, 0)
        .rect(19.0, 19.0, centered=True)
        .extrude(130.0)  # extrude along Y (positive W direction)
    )

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
