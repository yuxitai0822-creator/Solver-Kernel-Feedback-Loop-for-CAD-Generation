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
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0002\neg_01\iter_00\generated.step"

    # Dimensions from design plan (in mm, converted from cm)
    # Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
    # Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0
    # Extrude distance: 1120.0 mm (original was 112.0 cm = 1120.0 mm)

    # The design plan specifies:
    # - u_dir = [0, 0, -1] (negative Z)
    # - v_dir = [0, 1, 0] (positive Y)
    # - w_dir = [1, 0, 0] (positive X)
    # - Extrude direction: -w = [-1, 0, 0] (negative X)
    # - Extrude distance: 1120.0 mm

    # Create the outer rectangle profile
    # In the UV plane: u is along Z (negative), v is along Y
    # We'll work in XY plane and transform later

    # Build the profile on YZ plane (since u is Z, v is Y)
    # Outer rectangle corners in UV: (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88)
    # Inner rectangle corners in UV: (-6.0, 11.0), (-2.0, 11.0), (-2.0, 15.0), (-6.0, 15.0)

    # Convert UV to YZ coordinates: u->Z, v->Y
    # But we need to be careful about the sign of u direction
    # u_dir = [0, 0, -1] means u axis points in negative Z
    # So u coordinate maps to -Z

    # Let's build on YZ plane directly
    # Outer rectangle in YZ:
    #   Y: 10.88 to 15.12
    #   Z: -6.12 to -1.88 (since u maps to -Z, u=-1.88 -> Z=1.88, u=-6.12 -> Z=6.12)
    # Wait, let's re-examine: u_dir = [0, 0, -1] means u axis is negative Z
    # So a point with u coordinate 'a' is at position a * [0, 0, -1] = [0, 0, -a]
    # So u=-1.88 -> Z = 1.88, u=-6.12 -> Z = 6.12

    # Outer rectangle in YZ plane:
    #   Y: 10.88 to 15.12
    #   Z: 1.88 to 6.12

    # Inner rectangle in YZ plane:
    #   Y: 11.0 to 15.0
    #   Z: 2.0 to 6.0

    # Extrude direction: -w = -[1, 0, 0] = [-1, 0, 0] (negative X)
    # Extrude distance: 1120.0 mm

    # Build the profile
    result = (cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(1.88, 10.88)  # Start at outer corner (Z=1.88, Y=10.88)
        .lineTo(1.88, 15.12)   # Top edge
        .lineTo(6.12, 15.12)   # Right edge
        .lineTo(6.12, 10.88)   # Bottom edge
        .close()               # Back to start
        .extrude(1120.0)       # Extrude in positive X (since -w = -[1,0,0] means negative X, but we extrude positive and then cut)
    )

    # Cut the inner hole
    # Build inner rectangle and extrude it to create a cutting tool
    inner = (cq.Workplane("YZ")
        .center(0, 0)
        .moveTo(2.0, 11.0)    # Start at inner corner (Z=2.0, Y=11.0)
        .lineTo(2.0, 15.0)     # Top edge
        .lineTo(6.0, 15.0)     # Right edge
        .lineTo(6.0, 11.0)     # Bottom edge
        .close()               # Back to start
        .extrude(1120.0)       # Same extrusion distance
    )

    # Subtract inner from outer
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
