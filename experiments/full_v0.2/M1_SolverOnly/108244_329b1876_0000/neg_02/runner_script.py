import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Create a rectangular plate based on the design plan.
    # The profile is a rectangle with dimensions:
    #   length_u = 1219.2 mm (along u-axis, which is x-axis)
    #   width_v  = 2590.8 mm (along v-axis, which is z-axis, but we'll use y for simplicity)
    # The extrude distance is 44.45 mm along w-axis (y-axis).
    # The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0].
    # We'll create the rectangle in the XY plane (x = u, y = -v to match v_dir = [0,0,-1]? Actually v_dir is [0,0,-1] meaning v points along negative z.
    # But for simplicity, we can create the rectangle in the XY plane and extrude along Y.
    # The rectangle corners in uv: start_uv = (121.17356129030935, 31.299551148092803) and end_uv = (-0.7464387096940412, 290.379551148076).
    # The span in u is 121.17356129030935 - (-0.7464387096940412) = 121.92? Actually 121.17356129030935 + 0.7464387096940412 = 121.92, but expected length_u = 1219.2. 
    # Wait, the design plan says length_u = 1219.2, but the uv coordinates are around 121 and 0.7. This suggests the coordinates are in cm? The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the uv coordinates are in cm? Actually they are in mm after conversion? Let's check: 121.17356129030935 - (-0.7464387096940412) = 121.92 mm, but expected length_u = 1219.2 mm. That's a factor of 10. So the uv coordinates are in cm? The unit_conversion_applied says cm_to_mm (x10), meaning the original was in cm and multiplied by 10 to get mm. So the uv coordinates are already in mm? 121.92 mm vs 1219.2 mm — still off by factor 10. 
    # Actually, looking at the dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm. The uv span from coordinates: u_span = 121.17356129030935 - (-0.7464387096940412) = 121.92 mm. v_span = 290.379551148076 - 31.299551148092803 = 259.08 mm. So the uv coordinates are exactly 1/10 of the expected dimensions. This matches the unit_conversion_applied: cm_to_mm (x10) — the original sketch was in cm, and the coordinates are in cm? But the plan says unit is mm. The conversion was applied to dimensions, but the uv coordinates might still be in the original cm? Or maybe the uv coordinates are in mm but the dimensions are inferred from point span? Actually the dimensions are inferred from point span, so they should match. But they don't: 121.92 vs 1219.2. 
    # Let's re-read: "unit_conversion_applied": "cm_to_mm (x10)". This means the original design was in cm, and all values were multiplied by 10 to convert to mm. So the uv coordinates should also be multiplied by 10? But they are given as 121.173... which is 121.92 mm? Actually 121.173... is in mm? If original was in cm, then 12.1173 cm = 121.173 mm. So the uv coordinates are already in mm after conversion. Then the span is 121.92 mm, but expected length_u is 1219.2 mm. That's a factor of 10 discrepancy. 
    # Wait, maybe the uv coordinates are in the original cm? The plan says unit is mm, but the uv coordinates might be in the original unit before conversion? The compiler notes say "unit_conversion_applied: cm_to_mm (x10)", meaning the entire design was converted from cm to mm. So the uv coordinates should be in mm. But then the span is 121.92 mm, not 1219.2 mm. 
    # Let's check the width_v: v_span = 290.379551148076 - 31.299551148092803 = 259.08 mm. Expected width_v = 2590.8 mm. Again factor of 10. 
    # So the uv coordinates are in cm? Or the dimensions are wrong? The dimensions are "inferred_from_point_span", so they should be the span of the uv coordinates. But they are 10x larger. 
    # Perhaps the uv coordinates are in the original unit (cm) and the dimensions are in mm after conversion? That would make sense: uv in cm, dimensions in mm. So we need to scale the uv coordinates by 10 to get mm. 
    # Let's assume the uv coordinates are in cm (original unit) and we need to convert to mm by multiplying by 10. So the rectangle in mm: 
    #   u_min = -0.7464387096940412 * 10 = -7.464387096940412 mm
    #   u_max = 121.17356129030935 * 10 = 1211.7356129030935 mm
    #   v_min = 31.299551148092803 * 10 = 312.99551148092803 mm
    #   v_max = 290.379551148076 * 10 = 2903.79551148076 mm
    # Then u_span = 1211.7356129030935 - (-7.464387096940412) = 1219.2 mm (matches length_u)
    # v_span = 2903.79551148076 - 312.99551148092803 = 2590.8 mm (matches width_v)
    # So we need to scale the uv coordinates by 10.

    # The frame: u_dir = [1,0,0] (x-axis), v_dir = [0,0,-1] (negative z-axis), w_dir = [0,1,0] (y-axis).
    # So the rectangle lies in the xz-plane? Actually u is x, v is -z, so the profile is in the xz-plane (with v reversed).
    # The extrude direction is +w, which is +y.
    # So we create a rectangle in the xz-plane, then extrude along y.

    # Scale factor for uv coordinates (from cm to mm)
    scale = 10.0

    u_min = -0.7464387096940412 * scale
    u_max = 121.17356129030935 * scale
    v_min = 31.299551148092803 * scale
    v_max = 290.379551148076 * scale

    # The rectangle in uv space: u is x, v is -z (since v_dir = [0,0,-1]).
    # So we map: x = u, z = -v.
    # But careful: the rectangle corners are given in uv order. We'll create a wire from points.

    # Points in xz-plane:
    # Start at (u_min, -v_min) in xz? Actually we need to follow the curves.
    # The curves define a rectangle. Let's list the points in order:
    # Curve 0: start_uv = (121.17356129030935, 31.299551148092803) to end_uv = (-0.7464387096940412, 31.299551148092803)  -> horizontal line at v=31.2995, from u=121.1735 to u=-0.7464
    # Curve 1: start_uv = (121.17356129030935, 290.379551148076) to end_uv = (121.17356129030935, 31.299551148092803) -> vertical line at u=121.1735, from v=290.3795 to v=31.2995
    # Curve 2: start_uv = (-0.7464387096940412, 290.379551148076) to end_uv = (121.17356129030935, 290.379551148076) -> horizontal line at v=290.3795, from u=-0.7464 to u=121.1735
    # Curve 3: start_uv = (-0.7464387096940412, 31.299551148092803) to end_uv = (-0.7464387096940412, 290.379551148076) -> vertical line at u=-0.7464, from v=31.2995 to v=290.3795

    # So the rectangle corners in uv (u,v):
    # P1 = (121.17356129030935, 31.299551148092803)  (bottom-right?)
    # P2 = (-0.7464387096940412, 31.299551148092803) (bottom-left)
    # P3 = (-0.7464387096940412, 290.379551148076)   (top-left)
    # P4 = (121.17356129030935, 290.379551148076)    (top-right)

    # In xz-plane: x = u, z = -v (since v_dir = [0,0,-1])
    # So:
    # P1: x = 121.1735*scale, z = -31.2995*scale
    # P2: x = -0.7464*scale, z = -31.2995*scale
    # P3: x = -0.7464*scale, z = -290.3795*scale
    # P4: x = 121.1735*scale, z = -290.3795*scale

    # But note: the rectangle should be centered? Not necessarily. We'll just create the profile at z=0? Actually the profile is in the xz-plane, and we extrude along y.
    # The extrude distance is 44.45 mm along +y (w_dir = [0,1,0]).
    # So we create the rectangle in the xz-plane at y=0, then extrude to y=44.45.

    # Let's build the points in 3D (x, y, z):
    pts = [
        (u_max, 0, -v_min),  # P1
        (u_min, 0, -v_min),  # P2
        (u_min, 0, -v_max),  # P3
        (u_max, 0, -v_max),  # P4
    ]

    # Create a closed wire from these points
    wire = cq.Workplane("XZ").polyline(pts).close().wire()

    # Extrude along y-axis (positive direction) by 44.45 mm
    result = wire.extrude(44.45)

    # Export to STEP
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\108244_329b1876_0000\neg_02/generated.step")

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
