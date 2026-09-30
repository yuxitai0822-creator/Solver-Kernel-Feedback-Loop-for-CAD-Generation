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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0002\neg_01\iter_00\generated.step"

    # Design Plan parameters (converted from cm to mm where needed)
    # Outer rectangle: from UV coordinates (-6.12, 10.88) to (-1.88, 15.12)
    # Inner rectangle: from UV coordinates (-6.0, 11.0) to (-2.0, 15.0)
    # Extrude direction: -w (which is -x in world frame based on w_dir = [1,0,0])
    # Extrude distance: 1120.0 mm (from design plan, not the perturbed 1680)

    # Build on YZ plane since w_dir = [1,0,0] means extrusion along X
    # The profile is in the UV plane where u = -z, v = y (from frame definition)
    # So we sketch on YZ plane with coordinates (y, z)

    # Outer rectangle corners in (y, z):
    # (-1.88, 10.88) -> (-1.88, 15.12) -> (-6.12, 15.12) -> (-6.12, 10.88)
    # But note: u_dir = [0,0,-1] means u maps to -z, v_dir = [0,1,0] means v maps to y
    # So UV (u,v) -> world (x=?, y=v, z=-u)
    # The profile is at some x position, extruded along -x

    # Let's build the profile on YZ plane directly
    # Outer rectangle: y from 10.88 to 15.12, z from 1.88 to 6.12 (since u = -z, so z = -u)
    # Actually u = -z, so z = -u. For u = -1.88, z = 1.88; for u = -6.12, z = 6.12
    # v = y directly

    # Outer rectangle in (y,z):
    # Bottom-left: (10.88, 1.88)  -> y=10.88, z=1.88
    # Top-right: (15.12, 6.12)    -> y=15.12, z=6.12

    # Inner rectangle in (y,z):
    # Bottom-left: (11.0, 2.0)    -> y=11.0, z=2.0
    # Top-right: (15.0, 6.0)      -> y=15.0, z=6.0

    # Create the base workplane on YZ
    result = (cq.Workplane("YZ")
        # Outer rectangle
        .center(0, 0)
        .moveTo(10.88, 1.88)
        .lineTo(15.12, 1.88)
        .lineTo(15.12, 6.12)
        .lineTo(10.88, 6.12)
        .close()
        # Inner rectangle (cutout)
        .moveTo(11.0, 2.0)
        .lineTo(15.0, 2.0)
        .lineTo(15.0, 6.0)
        .lineTo(11.0, 6.0)
        .close()
        # Extrude along -x direction (since w_dir = [1,0,0], extrude direction = -w = [-1,0,0])
        .extrude(-1120.0)
    )

    # Export
    import cadquery as cq
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
