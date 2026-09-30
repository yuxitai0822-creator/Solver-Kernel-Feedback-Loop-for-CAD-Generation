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

    # Constants from design plan
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0002\neg_01\iter_01\generated.step"

    # Dimensions from design plan (in mm, converted from cm)
    # The design plan specifies:
    # - u_dir = [0, 0, -1] (negative Z)
    # - v_dir = [0, 1, 0] (positive Y)
    # - w_dir = [1, 0, 0] (positive X)
    # - Extrude direction: -w = [-1, 0, 0] (negative X)
    # - Extrude distance: 1120.0 mm

    # The UV coordinates are given in the design plan:
    # Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
    # Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0

    # The span along u should be 42.4 mm, along v should be 42.4 mm
    # This means the UV coordinates are in cm, not mm!
    # -6.12 to -1.88 = 4.24 cm = 42.4 mm
    # 10.88 to 15.12 = 4.24 cm = 42.4 mm

    # So we need to convert UV coordinates from cm to mm by multiplying by 10
    # Outer rectangle in UV (mm): u from -61.2 to -18.8, v from 108.8 to 151.2
    # Inner rectangle in UV (mm): u from -60.0 to -20.0, v from 110.0 to 150.0

    # Convert UV to YZ coordinates: u->Z, v->Y
    # u_dir = [0, 0, -1] means u axis points in negative Z
    # So u coordinate maps to -Z
    # u=-61.2 -> Z = 61.2, u=-18.8 -> Z = 18.8
    # u=-60.0 -> Z = 60.0, u=-20.0 -> Z = 20.0

    # Outer rectangle in YZ plane (mm):
    #   Y: 108.8 to 151.2
    #   Z: 18.8 to 61.2

    # Inner rectangle in YZ plane (mm):
    #   Y: 110.0 to 150.0
    #   Z: 20.0 to 60.0

    # Extrude direction: -w = -[1, 0, 0] = [-1, 0, 0] (negative X)
    # Extrude distance: 1120.0 mm

    # Build the outer profile
    result = (cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(18.8, 108.8)  # Start at outer corner (Z=18.8, Y=108.8)
        .lineTo(18.8, 151.2)   # Top edge
        .lineTo(61.2, 151.2)   # Right edge
        .lineTo(61.2, 108.8)   # Bottom edge
        .close()               # Back to start
        .extrude(1120.0)       # Extrude in positive X direction
    )

    # Build the inner profile for cutting
    inner = (cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(20.0, 110.0)  # Start at inner corner (Z=20.0, Y=110.0)
        .lineTo(20.0, 150.0)   # Top edge
        .lineTo(60.0, 150.0)   # Right edge
        .lineTo(60.0, 110.0)   # Bottom edge
        .close()               # Back to start
        .extrude(1120.0)       # Same extrusion distance
    )

    # Subtract inner from outer to create the hollow frame
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
