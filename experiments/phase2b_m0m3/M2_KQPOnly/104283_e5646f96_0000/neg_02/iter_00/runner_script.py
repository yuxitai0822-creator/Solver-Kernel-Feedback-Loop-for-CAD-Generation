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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0000\neg_02\iter_00\generated.step"

    # Design Plan parameters (converted from cm to mm where needed)
    # Profile: circle with center at (-15.0, 10.0) and radius 12.5 mm
    # Extrude: 75.0 mm along +w direction (which is +X in world frame)
    # The frame has u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
    # So w_dir is +X axis, meaning extrusion is along +X

    # Create workplane on YZ plane (since extrusion is along X)
    # The profile is defined in UV coordinates where U corresponds to -Z and V corresponds to +Y
    # So we need to map: U -> -Z, V -> +Y
    # Center in UV: (-15.0, 10.0) maps to world: Z = -(-15.0) = 15.0, Y = 10.0
    # But wait - the frame says u_dir = [0,0,-1] meaning U axis points in -Z direction
    # So a point at U coordinate u has world position: origin + u * u_dir + v * v_dir
    # Since origin is at bbox_min_corner, we need to be careful.
    # For simplicity, we'll create the circle on YZ plane centered at (10.0, 15.0) in (Y, Z)
    # and extrude along +X

    # Create workplane on YZ plane
    wp = cq.Workplane("YZ")

    # Create circle at center (Y=10.0, Z=15.0) with radius 12.5 mm
    # Note: In YZ plane, the coordinates are (Y, Z)
    circle = wp.center(10.0, 15.0).circle(12.5)

    # Extrude along +X direction (which is the normal of YZ plane) by 75.0 mm
    result = circle.extrude(75.0)

    # Export to STEP
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
