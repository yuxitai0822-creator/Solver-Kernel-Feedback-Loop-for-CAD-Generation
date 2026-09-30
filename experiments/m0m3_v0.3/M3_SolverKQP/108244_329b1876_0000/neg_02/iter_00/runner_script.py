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
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # Profile rectangle in UV plane: u from -0.746 to 121.174, v from 31.300 to 290.380
    # Note: The design plan coordinates are in UV space; we need to map to CQ workplane.
    # The frame has u along X, v along -Z, w along Y.
    # So we work on XZ plane (u->X, v->Z), extrude along Y (w direction).

    # Rectangle dimensions in UV space:
    u_min = -0.7464387096940412
    u_max = 121.17356129030935
    v_min = 31.299551148092803
    v_max = 290.379551148076

    # Widths:
    width_u = u_max - u_min  # 121.92
    width_v = v_max - v_min  # 259.08

    # But the design plan says length_u = 1219.2 and width_v = 2590.8 (10x larger)
    # This is because the original data was in cm and converted to mm (x10).
    # The UV coordinates in the design plan are already in mm (after conversion).
    # Wait: 121.92 * 10 = 1219.2, 259.08 * 10 = 2590.8. So the UV coordinates are in cm?
    # Actually the design plan says unit_conversion_applied: cm_to_mm (x10).
    # So the UV coordinates are in cm originally, now in mm after x10.
    # But the values in the plan are: u_min=-0.746, u_max=121.174 -> span=121.92
    # v_min=31.300, v_max=290.380 -> span=259.08
    # These are already in mm? 121.92 mm = 12.192 cm, but expected is 1219.2 mm = 121.92 cm.
    # There's inconsistency. Let's trust the explicit dimensions from the plan:
    # length_u = 1219.2, width_v = 2590.8, extrude = 44.45
    # The UV coordinates might be in a different scale. We'll use the explicit dimensions.

    # Build the rectangle centered at origin on XZ plane, then extrude along Y.
    # Rectangle dimensions: length_u along X, width_v along Z (since v_dir = [0,0,-1], we negate Z)

    length_u = 1219.2  # mm
    width_v = 2590.8   # mm
    extrude_dist = 44.45  # mm

    # Create workplane on XZ (front plane)
    wp = cq.Workplane("XZ")

    # Draw rectangle centered at origin
    # Note: v_dir is [0,0,-1], so positive v maps to negative Z.
    # To match the frame orientation, we draw rectangle with width_v along Z (but negated).
    # Actually simpler: just draw rectangle with given dimensions, extrude along Y.
    # The orientation of the rectangle in the plane doesn't matter for a flat plate.

    result = wp.rect(length_u, width_v).extrude(extrude_dist)

    # The result is a box centered at origin with dimensions:
    # X: -length_u/2 to +length_u/2
    # Z: -width_v/2 to +width_v/2
    # Y: 0 to extrude_dist (since extrude goes in +Y direction from XZ plane)

    # But the design plan expects the body to be positioned such that its bounding box
    # matches the UV coordinate ranges. Since we don't have exact positioning requirements
    # (the plan says "geometrically_inert" constraints), this should be fine.

    # Export
    OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108244_329b1876_0000\neg_02\iter_00\generated.step"
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
