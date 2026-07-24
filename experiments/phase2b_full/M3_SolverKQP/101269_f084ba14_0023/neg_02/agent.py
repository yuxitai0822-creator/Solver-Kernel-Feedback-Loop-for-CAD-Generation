import cadquery as cq

# Design Plan: extruded rectangle (basic slat v1)
# Dimensions: length_u = 95.25 mm, width_v = 571.5 mm, extrude_distance = 19.05 mm
# The profile is a rectangle in the UV plane, then extruded along W.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle vertices in UV: (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# Note: The UV coordinates given are 1/10 of the actual dimensions (since compiler notes say cm_to_mm x10).
# So we scale by 10: length_u = 95.25, width_v = 571.5.
# The rectangle is drawn in the XY plane (since u=x, v=z negative, but we can just use XY and then transform).
# Simpler: create a rectangle in XY plane, extrude along Z, then rotate to match frame.
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0). This means:
#   - X axis = u
#   - Y axis = w (since w_dir = (0,1,0))
#   - Z axis = -v (since v_dir = (0,0,-1))
# So the rectangle in UV maps to XZ plane? Let's just build in the frame directly.
# Use a workplane aligned with the frame: plane with normal = w_dir = (0,1,0).
# The rectangle lies in the plane spanned by u and v.
# So we create a workplane with normal (0,1,0), then draw rectangle of size length_u x width_v.
# But the UV coordinates start at (0,0) and go to (9.525, 57.15) which scaled by 10 gives (95.25, 571.5).
# The rectangle center will be at (95.25/2, 571.5/2) in that plane.

# Build:
result = (
    cq.Workplane("XY")
    .workplane(offset=0)
    .center(95.25/2, 571.5/2)
    .rect(95.25, 571.5)
    .extrude(19.05)
)

# Now rotate to match frame: we need u->X, v->Z (negative), w->Y.
# Current: rectangle in XY plane, extruded along Z.
# Desired: rectangle in XZ plane (u,v), extruded along Y (w).
# So rotate -90 deg around X axis to bring Z to Y? Let's think:
#   - Current: X=u, Y=v, Z=w (extrude direction)
#   - Desired: X=u, Y=w, Z=-v
# So we need to swap Y and Z, and negate Z.
# Rotation: rotate -90 deg around X axis: (x,y,z) -> (x, z, -y)
# This maps: X->X, Y->Z, Z->-Y. So after rotation:
#   - X = u (good)
#   - Y = w (good)
#   - Z = -v (good)
result = result.rotate((0,0,0), (1,0,0), -90)

# The rectangle was centered at (95.25/2, 571.5/2, 0) in original frame.
# After rotation, it will be at (95.25/2, 0, -571.5/2). We need to translate so that
# the min corner is at origin (since origin_convention is bbox_min_corner).
# The bbox after rotation: x from 0 to 95.25, y from 0 to 19.05, z from -571.5 to 0.
# To make min corner at origin, translate by (0, 0, 571.5).
result = result.translate((0, 0, 571.5))

# Now the part spans: u (X): 0 to 95.25, v (Z): 0 to 571.5, w (Y): 0 to 19.05.
# This matches the design plan.

cq.exporters.export(result, OUT_STEP_PATH)