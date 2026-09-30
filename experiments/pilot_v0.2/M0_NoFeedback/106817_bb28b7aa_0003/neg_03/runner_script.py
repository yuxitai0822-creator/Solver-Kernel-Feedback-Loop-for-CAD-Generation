import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded_circle (ruler holder w/screw)
    # The dimensions section provides the authoritative, scaled values:
    #   radius = 4.7117 mm (from explicit_dimension, unit_conversion_applied: cm_to_mm)
    #   center_uv = [50.800002, 63.500002] mm
    #   extrude_distance = 12.192 mm
    # The frame maps u->X, v->-Z, w->Y, so the extrusion goes along +Y.
    # The origin_convention is bbox_min_corner, so we offset the cylinder center
    # so that the bounding box minimum aligns with the origin.

    radius = 4.7117
    center_u = 50.800002
    center_v = 63.500002
    extrude_dist = 12.192

    # In the part_local frame (X, Y, Z):
    # u_dir = [1, 0, 0] -> X axis
    # v_dir = [0, 0, -1] -> -Z axis
    # w_dir = [0, 1, 0] -> Y axis
    # The circle lies in the u-v plane (X, -Z), centered at (center_u, center_v).
    # Extrusion is along +w (+Y) by extrude_dist.

    # To satisfy the bbox_min_corner origin convention:
    # Bounding box ranges:
    #   X: [center_u - radius, center_u + radius]
    #   Y: [0, extrude_dist]
    #   Z: [center_v - radius, center_v + radius] (since v maps to -Z)
    # We shift the center so that bbox_min is at (0, 0, 0):
    #   X_shift = -(center_u - radius) = radius - center_u
    #   Z_shift = -(center_v - radius) = radius - center_v

    x_shift = radius - center_u
    z_shift = radius - center_v

    # Build the cylinder
    result = (
        cq.Workplane("XZ")
        .center(x_shift, z_shift)
        .circle(radius)
        .extrude(extrude_dist)
    )

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
