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

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
    # Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
    # The rectangle in UV space: u from -0.746 to 121.174, v from 31.300 to 290.380
    # After scaling (cm->mm factor 10): u from -7.464 to 1211.736, v from 313.0 to 2903.8
    # But the design plan says length_u=1219.2, width_v=2590.8, extrude=44.45
    # The UV coordinates in the plan are in cm (original), so multiply by 10 for mm
    # u_min = -0.7464387096940412 * 10 = -7.464387096940412
    # u_max = 121.17356129030935 * 10 = 1211.7356129030935
    # v_min = 31.299551148092803 * 10 = 312.99551148092803
    # v_max = 290.379551148076 * 10 = 2903.79551148076
    # length_u = u_max - u_min = 1219.2 (matches)
    # width_v = v_max - v_min = 2590.8 (matches)
    # extrude = 44.45 mm (matches)

    # Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the profile is in XZ)
    # The frame: u along X, v along -Z, w along Y
    # So the rectangle is in XZ plane, extruded along Y

    # Create workplane on XZ
    wp = cq.Workplane("XZ")

    # Rectangle dimensions in mm (already converted)
    u_min = -7.464387096940412
    v_min = 312.99551148092803
    width_u = 1219.2  # u_max - u_min
    width_v = 2590.8  # v_max - v_min

    # Center of rectangle in UV space
    center_u = u_min + width_u / 2.0
    center_v = v_min + width_v / 2.0

    # Build rectangle on XZ plane
    # In XZ plane: u -> X, v -> Z (since v_dir is [0,0,-1], but we use positive Z for the rect)
    # Actually v_dir = [0,0,-1] means v axis points in -Z direction
    # So the rectangle coordinates: X = u, Z = -v
    # But for the rect function, we just need width and height, centered at (center_u, -center_v)
    # However, the rect function draws centered at the current point
    # So we move to the center and draw rect

    # Since v_dir is [0,0,-1], the v coordinate maps to -Z
    # So the center in XZ is (center_u, -center_v)
    result = wp.moveTo(center_u, -center_v).rect(width_u, width_v, centered=True).extrude(44.45)

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108244_329b1876_0000\neg_03\iter_00/generated.step"
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
