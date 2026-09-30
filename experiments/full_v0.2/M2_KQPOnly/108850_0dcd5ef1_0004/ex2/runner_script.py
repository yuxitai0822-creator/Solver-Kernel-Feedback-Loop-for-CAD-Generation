import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (flat plate)
    # Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
    # Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
    # Origin at bbox_min_corner, so we place the rectangle in the XY plane (u=x, v=z, w=y)
    # The profile is defined in uv space: u along x, v along z (since v_dir = (0,0,-1), we flip sign)
    # The rectangle vertices in uv: (0,0), (17.145,0), (17.145,11.0998), (0,11.0998)
    # Note: dimensions in plan are 171.45 and 110.998, but uv coordinates are scaled by 0.1? 
    # Actually the plan says unit_conversion_applied: cm_to_mm (x10), so the uv values are in cm? 
    # The explicit dimensions are 171.45 mm and 110.998 mm, so we use those directly.
    # The uv coordinates in the plan are 17.145 and 11.0998, which are 171.45/10 and 110.998/10.
    # So we must multiply by 10 to get mm.

    # Build the rectangle in the XY plane (x=u, y=w? No, w is extrusion direction)
    # Frame: u_dir = x, v_dir = -z, w_dir = y
    # So the profile lies in the xz-plane (u along x, v along -z).
    # We'll create a 2D sketch on the XZ plane, then extrude along Y.

    length_u = 171.45  # mm
    width_v = 110.998  # mm
    extrude_dist = 6.35  # mm

    # Create the rectangle centered at origin? The plan uses bbox_min_corner origin convention.
    # So the rectangle should start at (0,0,0) in the local frame.
    # In world: u=x, v=-z, w=y. So the rectangle lies in the plane y=0, with corners:
    # (0,0,0), (length_u,0,0), (length_u,0,-width_v), (0,0,-width_v)
    # But we can just create a rectangle in the XY plane and then rotate? Simpler: use workplane.

    result = (
        cq.Workplane("XZ")
        .rect(length_u, width_v, centered=False)
        .extrude(extrude_dist)
    )

    # The rect is created with lower-left corner at (0,0) in the workplane's local coordinates.
    # For XZ workplane, the local axes are X and Z. So the rectangle extends in +X and +Z.
    # But we need it to extend in +X and -Z (since v_dir = -z). So we need to flip the Z direction.
    # Alternatively, we can create the rectangle manually using vertices.

    # Let's do it properly with a polyline to ensure correct orientation.
    result = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(length_u, 0)
        .lineTo(length_u, -width_v)
        .lineTo(0, -width_v)
        .close()
        .extrude(extrude_dist)
    )

    # Now the extrusion direction is +Y (w_dir = y). This matches the plan.

    cq.exporters.export(result, OUT_STEP_PATH)

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
