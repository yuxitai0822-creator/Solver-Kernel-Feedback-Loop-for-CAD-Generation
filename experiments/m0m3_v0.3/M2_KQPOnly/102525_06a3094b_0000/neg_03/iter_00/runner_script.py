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

    # Design Plan: SOIC-8 body
    # Dimensions: 3.9 mm (u) x 4.9 mm (v) x 1.55 mm (w)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # Profile rectangle centered at origin in uv-plane

    # Build the rectangular profile
    # The profile is centered at (0,0) in the uv-plane
    # u spans from -1.95 to 1.95 (total 3.9 mm)
    # v spans from -2.45 to 2.45 (total 4.9 mm)

    # Create workplane on XZ plane (since v_dir = [0,0,-1] and w_dir = [0,1,0])
    # Actually, let's use XY plane and then rotate to match the frame
    # Simpler: just create the rectangle on XY and extrude along Z
    # Then rotate to match the specified frame orientation

    # The frame says:
    # u_dir = [1,0,0] (X axis)
    # v_dir = [0,0,-1] (negative Z axis)
    # w_dir = [0,1,0] (Y axis)
    # So the rectangle is in the XZ plane, extruded along Y

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Draw centered rectangle: 3.9 mm along X, 4.9 mm along Z
    # But v_dir is [0,0,-1], so the rectangle's v dimension is along Z
    # The profile coordinates in the design plan show:
    # start_uv: [0.195, -0.245] to [0.195, 0.245] etc.
    # These are half-dimensions: u_half=0.195*10=1.95, v_half=0.245*10=2.45
    # Wait, the design plan says unit conversion cm->mm x10
    # So the actual dimensions are 3.9 mm x 4.9 mm

    # Create the rectangle centered at origin
    result = wp.center(0, 0).rect(3.9, 4.9).extrude(1.55)

    # The extrusion direction is along Y (positive w_dir)
    # This gives us a rectangular prism with:
    # - X span: 3.9 mm (u direction)
    # - Z span: 4.9 mm (v direction)
    # - Y span: 1.55 mm (w direction)

    # Export to STEP
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0000\neg_03\iter_00/generated.step"
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
