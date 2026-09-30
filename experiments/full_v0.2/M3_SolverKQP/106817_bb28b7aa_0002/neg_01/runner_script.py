import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: thumb screw (disk)
    # Extruded circle with radius 4.87045 mm and height 6.8707 mm
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # The circle center in UV is at (11.430000364780426, 0.0) but that is in the profile's UV space.
    # The profile radius is 4.87045 mm (from dimensions).
    # The extrude distance is 6.8707 mm along +w direction.
    # We'll create a circle centered at (0,0) in the XY plane, then extrude along Z.
    # Then we'll rotate/translate to match the specified frame.

    # Step 1: Create the base circle at origin in XY plane
    result = (cq.Workplane("XY")
              .circle(4.87045)  # radius from dimensions
              .extrude(6.8707)   # extrude distance
             )

    # Step 2: Apply transformation to match the specified frame.
    # The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
    # This means: local X (u) = world X, local Y (v) = -world Z, local Z (w) = world Y.
    # So we need to rotate the part so that original Z (extrude direction) aligns with world Y.
    # Original: circle in XY, extrude along Z.
    # Desired: circle in XZ plane? Actually v_dir = (0,0,-1) means the profile's v axis is -Z.
    # The profile lies in the plane spanned by u and v, so the profile plane is XZ (with v reversed).
    # Extrude direction is +w = (0,1,0) = world Y.
    # So we need to rotate: original Z -> world Y, original Y -> world -Z (since v_dir = -Z).
    # This is a rotation of -90 degrees around X axis.
    # Let's apply: rotate around X by -90 degrees.
    result = result.rotate((0,0,0), (1,0,0), -90)

    # Step 3: The profile center_uv is at (11.430000364780426, 0.0) in UV space.
    # But the dimensions show radius 4.87045 and center_uv (114.300004, 0.0) — note the discrepancy.
    # The compiler notes say unit conversion cm_to_mm (x10). So original center was 11.43 mm? 
    # Actually the profile center_uv is (11.430000364780426, 0.0) and dimensions show (114.300004, 0.0).
    # The radius in dimensions is 4.87045, which matches the profile radius 0.48704499999999984 * 10? 
    # Wait: profile radius is 0.48704499999999984, dimensions radius is 4.87045. 
    # The compiler says cm_to_mm (x10). So original radius was 0.48704499999999984 cm = 4.87045 mm. Good.
    # The center_uv in profile is (11.430000364780426, 0.0) — that's in mm? 
    # But dimensions show (114.300004, 0.0) — that's 10x. So the profile center is 11.43 mm in UV.
    # However, the part is a disk (cylinder) and the center offset might be intentional.
    # But the validation expects span_u = 9.7409 (diameter = 2*4.87045 = 9.7409) and span_v = 9.7409.
    # If we offset the circle, the span would be larger. So the center should be at origin for a centered disk.
    # The profile center_uv might be a misalignment or the part is not centered? 
    # But the part_category is "disk" which implies centered. The validation expects span 9.7409 in u and v.
    # If the circle is offset by 11.43 mm, the span would be from 11.43-4.87=6.56 to 11.43+4.87=16.30, span=9.74.
    # Actually span is still 9.74 because it's the extent of the shape along the axis, not the position.
    # So the offset doesn't affect span. But the part would be off-center.
    # The design plan says origin_convention is bbox_min_corner, so the part's bounding box min corner is at origin.
    # That means the part should be positioned so its min corner is at (0,0,0).
    # For a cylinder of radius 4.87045 and height 6.8707, if centered at origin, min corner would be at (-4.87045, -4.87045, 0).
    # But bbox_min_corner convention means the whole part's bbox min is at origin.
    # So we need to translate so that the min corner is at (0,0,0).
    # Let's compute: after rotation, the cylinder is along Y axis. The circle is in XZ plane.
    # The cylinder extends from y=0 to y=6.8707 (since extrude from 0 to +6.8707).
    # The circle is centered at (0,0) in XZ, so the cylinder spans x from -4.87045 to 4.87045, z from -4.87045 to 4.87045.
    # So bbox min is (-4.87045, 0, -4.87045). To make min corner at origin, translate by (4.87045, 0, 4.87045).
    result = result.translate((4.87045, 0, 4.87045))

    # Export
    cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\106817_bb28b7aa_0002\neg_01/generated.step")

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
