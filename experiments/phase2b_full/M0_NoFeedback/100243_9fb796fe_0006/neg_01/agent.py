import cadquery as cq

# Create a rectangular profile in the UV plane
# The profile is a 19mm x 19mm square centered at the origin
# The rectangle corners are at (-9.5, -9.5) and (9.5, 9.5)
# But the design plan specifies the rectangle in UV coordinates with specific values.
# The UV coordinates given: 
#   start_uv: [-58.27820137826746, -12.04014576968157]
#   end_uv:   [-56.37820137826746, -13.940145769681571]
# This is a 2mm x 1.9mm rectangle? Let's check:
#   u range: -58.2782 to -56.3782 = 1.9 mm
#   v range: -12.0401 to -13.9401 = -1.9 mm (absolute 1.9 mm)
# So it's a 1.9mm x 1.9mm square, but the dimensions say 19mm x 19mm.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
# So the UV coordinates are in cm? Actually the values are -58.278... which is huge.
# Let's re-interpret: The rectangle is 19mm x 19mm. The UV coordinates given
# are just the corners of a 19x19 square somewhere in UV space.
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0].
# So u = x, v = -z, w = y.
# The rectangle spans from u=-58.2782 to u=-56.3782 (delta=1.9) and v=-13.9401 to v=-12.0401 (delta=1.9).
# But the expected span is 19mm. So the UV coordinates are in cm? 
# Actually 1.9 cm = 19 mm. So the UV coordinates are in cm, and we need to scale by 10.
# But the design plan says unit is mm. The compiler notes say cm_to_mm (x10).
# So the original source was in cm, and the values were multiplied by 10 to get mm.
# But the UV coordinates shown are -58.278... which if multiplied by 10 would be -582.78...
# That doesn't match. Let's just use the explicit dimensions: 19mm x 19mm.
# The rectangle center is at the midpoint of the UV coordinates.
# Midpoint u: (-58.27820137826746 + -56.37820137826746)/2 = -57.32820137826746
# Midpoint v: (-12.04014576968157 + -13.940145769681571)/2 = -12.99014576968157
# So the rectangle is centered at (-57.3282, -12.9901) in UV space.
# But for simplicity, we'll create the rectangle centered at the origin and then translate.
# Actually, the extrude direction is +w, which is +y.
# The extrude distance is 130mm.

# Let's build the profile in the UV plane (which is xz plane since u=x, v=-z).
# We'll create a rectangle centered at the origin with size 19mm x 19mm.
# Then we'll extrude it 130mm in the +y direction.

# But the design plan specifies the rectangle location in UV space.
# The rectangle corners are at:
#   (-58.27820137826746, -12.04014576968157)  -> top-left?
#   (-58.27820137826746, -13.940145769681571) -> bottom-left
#   (-56.37820137826746, -13.940145769681571) -> bottom-right
#   (-56.37820137826746, -12.04014576968157)  -> top-right
# This is a 1.9 x 1.9 square in UV space. But the dimensions say 19mm.
# The compiler notes say cm_to_mm (x10). So the UV coordinates are in cm?
# If we multiply by 10: -582.782... to -563.782... that's 19mm.
# So the UV coordinates are in cm, and we need to scale by 10 to get mm.
# But the design plan says unit is mm. This is confusing.
# Let's just use the explicit dimensions: 19mm x 19mm.
# The location in space: the rectangle is at some position.
# The frame origin is at the bbox min corner. So the rectangle is at some offset.
# We'll place the rectangle such that its center is at the midpoint of the UV coordinates.
# Midpoint u: (-58.27820137826746 + -56.37820137826746)/2 = -57.32820137826746
# Midpoint v: (-12.04014576968157 + -13.940145769681571)/2 = -12.99014576968157
# But these are in cm? If we multiply by 10: -573.282... and -129.901...
# That seems too large. Let's just use the values as mm and create a 19mm square.
# The rectangle spans from u=-58.2782 to u=-56.3782, which is 1.9mm, not 19mm.
# So there's a discrepancy. The dimensions say 19mm, but the UV coordinates give 1.9mm.
# The compiler notes say cm_to_mm (x10). So the original was 1.9cm = 19mm.
# So the UV coordinates are in cm, and we need to multiply by 10 to get mm.
# Let's scale the UV coordinates by 10.

scale = 10.0
# Scaled corners:
# (-582.7820137826746, -120.4014576968157)
# (-582.7820137826746, -139.4014576968157)
# (-563.7820137826746, -139.4014576968157)
# (-563.7820137826746, -120.4014576968157)
# Center: (-573.2820137826746, -129.9014576968157)
# Size: 19mm x 19mm

# But this places the rectangle far from origin. That's fine.
# The extrude direction is +w = +y, distance 130mm.

# Let's build the rectangle in the xz plane (u=x, v=-z).
# We'll create a rectangle centered at (center_u, 0, -center_v) because v = -z.
# Actually, v_dir = [0,0,-1], so v = -z. So z = -v.
# The rectangle in 3D: 
#   x from -582.782 to -563.782
#   z from -(-139.401) to -(-120.401) = 139.401 to 120.401? 
#   Actually v = -z, so z = -v.
#   v ranges from -139.401 to -120.401, so z ranges from 139.401 to 120.401.
#   That's a decreasing z range. The rectangle is 19mm in z as well.

# Let's just create the rectangle using the scaled UV coordinates.
# We'll use a workplane in the xz plane.

# Create the rectangle profile
# The rectangle corners in UV (scaled):
#   (-582.7820137826746, -120.4014576968157)
#   (-582.7820137826746, -139.4014576968157)
#   (-563.7820137826746, -139.4014576968157)
#   (-563.7820137826746, -120.4014576968157)
# In 3D (x, z):
#   x: -582.782 to -563.782
#   z: 120.401 to 139.401 (since z = -v, and v is negative)

# Let's compute:
# v1 = -120.4014576968157 -> z1 = 120.4014576968157
# v2 = -139.4014576968157 -> z2 = 139.4014576968157
# So z ranges from 120.401 to 139.401, which is 19mm.

# We'll create the rectangle using a polyline.

# Define points in 3D (x, y, z) where y=0 for the profile
p1 = (-582.7820137826746, 0, 120.4014576968157)
p2 = (-582.7820137826746, 0, 139.4014576968157)
p3 = (-563.7820137826746, 0, 139.4014576968157)
p4 = (-563.7820137826746, 0, 120.4014576968157)

# Create the profile as a wire
pts = [p1, p2, p3, p4]
wire = cq.Workplane("XY").polyline(pts).close().wire()

# Extrude in the +y direction (w_dir = [0,1,0])
result = wire.extrude(130.0)

# Export
cq.exporters.export(result, OUT_STEP_PATH)