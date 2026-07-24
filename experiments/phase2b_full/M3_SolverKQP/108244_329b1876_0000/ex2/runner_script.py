import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate/panel)
    # Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
    # The profile is a rectangle in the UV plane, then extruded along +W direction.
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The rectangle corners in UV: 
    #   start_uv = (121.17356129030935, 31.299551148092803)
    #   end_uv = (-0.7464387096940412, 290.379551148076)
    # We'll compute width and height from these points.

    # Compute rectangle dimensions in UV space:
    # u_min = -0.7464387096940412, u_max = 121.17356129030935
    # v_min = 31.299551148092803, v_max = 290.379551148076
    # width_u = u_max - u_min = 121.92, height_v = v_max - v_min = 259.08
    # But the design plan says length_u = 1219.2, width_v = 2590.8 (note: 10x scaling from cm to mm?)
    # The compiler notes say unit_conversion_applied: cm_to_mm (x10).
    # So the UV values are in cm? Actually the plan says unit is mm, but the UV coordinates are small.
    # The inferred dimensions are 1219.2 and 2590.8, which are exactly 10x the UV spans (121.92 and 259.08).
    # So we must scale the UV coordinates by 10 to get mm.
    # Alternatively, we can directly use the inferred dimensions.

    # Let's use the inferred dimensions directly for clarity and robustness.
    length_u = 1219.2  # mm
    width_v = 2590.8   # mm
    extrude_distance = 44.45  # mm

    # Create the rectangle centered at origin? The plan uses bbox_min_corner origin convention.
    # The UV coordinates suggest the rectangle is offset. But for simplicity and to match the span,
    # we can create a rectangle from (0,0) to (length_u, width_v) in the UV plane.
    # However, the frame has v_dir = (0,0,-1), so v axis points downward in Z.
    # We'll create the rectangle in the XY plane (since u_dir = X, v_dir = -Z, w_dir = Y).
    # Actually: u_dir = (1,0,0) = X, v_dir = (0,0,-1) = -Z, w_dir = (0,1,0) = Y.
    # So the profile lies in the X-Z plane (with v = -Z), and extrude along Y.

    # To keep it simple, we'll create a box directly with the correct dimensions.
    # But the design plan specifies an extruded rectangle, so we'll follow that.

    # Create the rectangle in the XY plane (we'll rotate later if needed).
    # Actually, let's just create a box with the correct dimensions and orientation.
    # The frame: u = X, v = -Z, w = Y. So the plate spans X (1219.2), Z (2590.8), and Y (44.45).
    # But the extrude direction is +w = +Y, so the plate is thin in Y.

    # Let's create a workplane on the XZ plane (since v = -Z, we can use the XZ plane).
    # We'll create a rectangle in XZ, then extrude in Y.

    result = (cq.Workplane("XZ")
              .rect(length_u, width_v)
              .extrude(extrude_distance))

    # Export to STEP
    cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108244_329b1876_0000\\ex2/generated.step")

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
