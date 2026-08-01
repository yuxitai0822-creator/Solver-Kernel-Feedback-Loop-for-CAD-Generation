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

    # Design Plan: extruded rectangle 1930 x 550 mm, extrude 50 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # This means sketch on XZ plane (u along X, v along -Z), extrude along Y (+w)
    # Rectangle in UV: (0,0) to (193,55) but dimensions say 1930 x 550 mm
    # The UV coordinates are scaled by 10 (cm to mm conversion)
    # So rectangle is 1930 x 550 mm

    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0002\neg_01\iter_00\generated.step"

    # Build the rectangle on XZ plane (since v_dir is -Z, we use XZ plane)
    # The rectangle corners in UV: (0,0) to (193,55) -> scaled to (0,0) to (1930,550)
    # But the frame has v_dir = [0,0,-1], so v coordinate maps to -Z
    # To get positive Z, we can negate the v coordinate or use XY plane
    # Simpler: use Workplane("XY") and rotate as needed
    # Actually, let's use the frame directly:
    # u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
    # So sketch plane is XZ (normal = Y), but v goes negative Z
    # We'll create on XY plane and then rotate, or just use XZ plane with correct orientation

    # Create workplane on XZ plane (normal = Y)
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at (1930/2, 550/2) = (965, 275) in UV space
    # But v_dir = [0,0,-1], so v=0 maps to Z=0, v=550 maps to Z=-550
    # To get positive Z, we can offset: center at (965, -275) and negate v
    # Or simpler: just draw on XY plane and extrude along Z, then rotate
    # Let's use XY plane for simplicity, then rotate to match frame

    # Actually, the simplest: use Workplane("XY") and draw rectangle
    # Then extrude along Z, and rotate 90 degrees around X to match frame
    # But the design plan expects the part in the frame orientation
    # Let's just build it directly on XZ plane with correct dimensions

    # Rectangle in UV: (0,0) to (1930, 550)
    # On XZ plane: X = u, Z = -v (since v_dir = [0,0,-1])
    # So corners: (0,0,0), (1930,0,0), (1930,0,-550), (0,0,-550)
    # Center: (965, 0, -275)

    # Build rectangle on XZ plane
    wp = cq.Workplane("XZ")
    rect = wp.moveTo(965, -275).rect(1930, 550, centered=True)

    # Extrude along Y (w_dir = [0,1,0]) by 50 mm
    result = rect.extrude(50.0)

    # Export
    exporters.export(result, OUT_STEP_PATH)
    print(f"Exported to {OUT_STEP_PATH}")

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
