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

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0007\neg_01\iter_00/generated.step"

    # Design Plan dimensions (in mm):
    # Rectangle: 279.4 mm (u) x 50.8 mm (v)
    # Extrude: 19.05 mm (w direction)
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means the sketch is in the XZ plane (u=X, v=Z), extrude along Y (w=Y)

    # Build the rectangle in the XZ plane
    # The rectangle spans from (0,0) to (279.4, 50.8) in UV coordinates
    # U maps to X, V maps to Z (since v_dir=[0,0,-1], we negate Z)
    # So in XZ: x from 0 to 279.4, z from -50.8 to 0

    # Create workplane on XZ plane
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at (139.7, -25.4) with width 279.4 and height 50.8
    # This matches the UV coordinates: u in [0, 279.4], v in [0, 50.8]
    # v_dir = [0,0,-1] means v maps to -z, so v=0 -> z=0, v=50.8 -> z=-50.8
    result = wp.moveTo(139.7, -25.4).rect(279.4, 50.8, centered=True).extrude(19.05)

    # Export
    importers = None
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
