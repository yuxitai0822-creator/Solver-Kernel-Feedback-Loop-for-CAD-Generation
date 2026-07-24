import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
    import cadquery as cq

    # Design Plan: extruded rectangle (square strut)
    # Profile: rectangle 19mm x 19mm (in u-v plane)
    # Extrude: 130mm along +w direction
    # Frame: u = (1,0,0), v = (0,0,-1), w = (0,1,0)
    # Origin at bbox_min_corner: profile center offset to match uv coordinates

    # The profile vertices in uv space:
    #   (-58.27820137826746, -12.04014576968157)  -> bottom-left
    #   (-58.27820137826746, -13.940145769681571) -> top-left? Actually v negative direction
    #   (-56.37820137826746, -13.940145769681571) -> top-right
    #   (-56.37820137826746, -12.04014576968157)  -> bottom-right
    # Width in u: 2.0 mm (from -58.2782 to -56.3782)
    # Width in v: 1.9 mm (from -13.9401 to -12.0401) but expected 19mm? 
    # The dimensions say length_u=19, width_v=19. The uv coordinates seem scaled by 0.1?
    # Actually note: unit_conversion_applied: cm_to_mm (x10). So original cm values *10 = mm.
    # The uv coordinates are in mm after conversion? Let's check: 
    #   u range: -58.2782 to -56.3782 = 1.9 mm? That's 1.9 not 19.
    #   v range: -13.9401 to -12.0401 = 1.9 mm? That's 1.9 not 19.
    # But dimensions say 19mm. Possibly the uv coordinates are in cm before conversion?
    # The conversion note says cm_to_mm (x10). So original cm values *10 = mm.
    # If original uv in cm: -5.82782 to -5.63782 = 0.19 cm = 1.9 mm? Still not 19.
    # Let's trust the explicit dimensions: 19mm x 19mm x 130mm.
    # The uv coordinates likely represent a 19x19 rectangle centered somewhere.
    # Actually: -58.2782 to -56.3782 = 1.9? That's 1.9 not 19. 
    # Wait: -58.27820137826746 to -56.37820137826746 = 1.900000000000002 mm? 
    # That's 1.9 mm, not 19. But the dimension says 19.0 mm.
    # Possibly the uv coordinates are in the original cm and we need to scale?
    # Or maybe the rectangle is 19mm but the uv coordinates are just the corner positions?
    # Let's compute: -58.2782 - (-56.3782) = -1.9? Actually 56.3782 - 58.2782 = -1.9, absolute 1.9.
    # So width in u is 1.9 mm. But dimension says 19.0 mm. 
    # This suggests the uv coordinates are in cm (before *10 conversion).
    # So original cm: u from -5.82782 to -5.63782 = 0.19 cm = 1.9 mm? Still not 19.
    # Hmm. Let's re-read: "unit_conversion_applied: cm_to_mm (x10)". 
    # The uv coordinates are given in mm after conversion? Or before?
    # The design plan says unit: mm. So uv coordinates should be in mm.
    # But 1.9 mm vs 19 mm dimension. Something is off.
    # Let's just use the explicit dimensions: 19x19x130 and place the rectangle centered at origin.
    # The frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0). So u is x, v is -z, w is y.
    # We'll create a rectangle in the xz-plane (u-v) and extrude along y (w).

    # Create the rectangle profile centered at origin (since no explicit position given, we center it)
    # The uv coordinates suggest a specific location, but we'll use the dimensions.
    # Actually, let's use the uv coordinates as given but scaled to match 19mm.
    # The uv range is 1.9, but we need 19. So scale factor 10.
    # Or maybe the uv coordinates are already in mm and the rectangle is 1.9mm? 
    # But the dimension says 19mm. Let's trust the dimension.
    # I'll create a 19x19 rectangle centered at the midpoint of the uv coordinates.

    # Midpoint of uv coordinates:
    mid_u = (-58.27820137826746 + -56.37820137826746) / 2.0  # = -57.32820137826746
    mid_v = (-12.04014576968157 + -13.940145769681571) / 2.0  # = -12.99014576968157

    # But we'll just create a rectangle centered at origin for simplicity, 
    # then translate to match the uv center? Actually the design plan says 
    # origin_convention: bbox_min_corner. So the origin is at the minimum corner of the bounding box.
    # The uv coordinates likely represent the profile in the local frame.
    # Let's just create the rectangle with the given dimensions and place it so that 
    # the bbox min corner is at origin.

    # Since the rectangle is 19x19, we can place it with one corner at (0,0) in uv plane.
    # But the uv coordinates show negative values, so the rectangle is in negative quadrant.
    # Let's just use the uv coordinates directly (they define the profile shape and position).
    # The width in u is 1.9, but we need 19. So scale by 10.

    # Actually, I think the uv coordinates are in the original cm units before conversion.
    # After cm->mm conversion (x10), the rectangle becomes 19mm x 19mm.
    # So we should scale the uv coordinates by 10 to get mm.

    scale = 10.0
    pts_uv = [
        (-58.27820137826746 * scale, -12.04014576968157 * scale),
        (-58.27820137826746 * scale, -13.940145769681571 * scale),
        (-56.37820137826746 * scale, -13.940145769681571 * scale),
        (-56.37820137826746 * scale, -12.04014576968157 * scale),
    ]

    # Create the profile as a wire
    # We'll use the uv coordinates directly in the u-v plane (x and -z axes)
    # u -> x, v -> -z

    # Build the rectangle in 3D space
    # Points in 3D: (u, 0, -v) because v direction is (0,0,-1)
    pts_3d = [(u, 0, -v) for u, v in pts_uv]

    # Create the profile wire
    rect = cq.Workplane("XY").polyline(pts_3d).close().extrude(130.0)

    # But this might not be correct. Let's use a simpler approach:
    # Create a rectangle in the XY plane, then rotate to align with the frame.
    # Frame: u=(1,0,0)=x, v=(0,0,-1)=-z, w=(0,1,0)=y
    # So the profile is in the x-z plane (u-v), extrude along y (w).

    # Let's create the rectangle in the XZ plane (since u=x, v=-z, so v is along -z)
    # The rectangle dimensions: length_u=19, width_v=19
    # We'll center it at the midpoint of the uv coordinates (scaled)

    # Actually, let's just use the explicit dimensions and place the rectangle 
    # such that its bbox min corner is at origin (as per origin_convention).
    # The uv coordinates give the location: min u = -582.782, min v = -139.4015
    # So the rectangle extends from u=-582.782 to u=-563.782 (width 19)
    # and v=-139.4015 to v=-120.4015 (width 19)
    # In 3D: x from -582.782 to -563.782, z from 139.4015 to 120.4015 (since v=-z)

    # Let's build it properly:

    # Create the rectangle in the XZ plane
    # Points: (x, 0, z)
    # x from -582.782 to -563.782
    # z from 120.4015 to 139.4015 (since v=-z, and v ranges from -139.4 to -120.4)

    x_min = -58.27820137826746 * 10  # -582.782
    x_max = -56.37820137826746 * 10  # -563.782
    y_min = 0
    y_max = 130.0  # extrude distance
    z_min = 12.04014576968157 * 10   # 120.4015 (since v=-z, v=-12.04 => z=120.4)
    z_max = 13.940145769681571 * 10  # 139.4015

    # Actually, v direction is (0,0,-1), so v coordinate maps to -z.
    # v = -12.04 => z = 12.04? No: v = -z, so z = -v.
    # v = -12.04 => z = 12.04
    # v = -13.94 => z = 13.94
    # So z ranges from 12.04 to 13.94 (scaled: 120.4 to 139.4)

    # Let's just create the box directly:
    result = cq.Workplane("XY").box(19.0, 130.0, 19.0, centered=(False, False, False))
    # This creates a box with corner at origin, dimensions: x=19, y=130, z=19
    # But we need to position it at the correct location.
    # The uv coordinates indicate the rectangle is at negative x and positive z.
    # Let's translate:
    result = result.translate((x_min, 0, z_min))

    # Actually, let's verify: box(19,130,19, centered=False) creates a box from (0,0,0) to (19,130,19)
    # We want it from (x_min, 0, z_min) to (x_max, 130, z_max)
    # So translate by (x_min, 0, z_min)

    # But wait, the extrude direction is +w = (0,1,0) = y. So the box should extend along y from 0 to 130.
    # That matches.

    # Let's use the correct approach: create the profile in the u-v plane and extrude.
    # Using the frame: u=x, v=-z, w=y
    # Profile is a rectangle in uv space: u from -582.782 to -563.782, v from -139.4015 to -120.4015
    # In 3D: x from -582.782 to -563.782, z from 139.4015 to 120.4015 (since z = -v)

    # Create the profile as a 2D sketch in the XZ plane
    # We'll use Workplane with the correct plane

    # Actually, let's use the simplest approach that matches the dimensions:
    # Create a 19x19 rectangle in the XZ plane, then extrude 130 in Y direction.
    # Position it according to the uv coordinates.

    # The uv coordinates after scaling:
    # u_min = -582.782, u_max = -563.782 (width 19)
    # v_min = -139.4015, v_max = -120.4015 (width 19)
    # In 3D: x = u, z = -v
    # So x_min = -582.782, x_max = -563.782
    # z_min = 120.4015, z_max = 139.4015

    # Create the rectangle in the XZ plane
    rect = (
        cq.Workplane("XZ")
        .center((x_min + x_max)/2, (z_min + z_max)/2)  # center of rectangle
        .rect(19.0, 19.0)
        .extrude(130.0)  # extrude along Y (normal to XZ plane)
    )

    # But extrude from XZ plane goes along Y, which is correct (w direction).
    # However, the extrude direction should be +w = +y, and the rectangle should be at y=0 to y=130.
    # The above creates a rectangle centered at (center_x, center_z) in XZ plane, 
    # then extrudes along Y. But the extrusion will be centered at y=0? 
    # Actually, Workplane("XZ") places the workplane at y=0. 
    # The rect is drawn on that plane, then extruded along the normal (y).
    # By default, extrude goes both ways? No, extrude goes in the positive normal direction by default.
    # So it will extrude from y=0 to y=130. That's correct.

    # But we need the rectangle to be positioned correctly in x and z.
    # The center of the rectangle in uv space:
    center_u = (x_min + x_max) / 2.0  # = -573.282
    center_v = (v_min + v_max) / 2.0  # = -129.9015
    # In 3D: center_x = center_u = -573.282, center_z = -center_v = 129.9015

    # So:
    result = (
        cq.Workplane("XZ")
        .center(-573.2820133782675, 129.90145769568157)
        .rect(19.0, 19.0)
        .extrude(130.0)
    )

    # Export
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
