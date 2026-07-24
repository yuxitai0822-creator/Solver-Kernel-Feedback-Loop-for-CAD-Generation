import cadquery as cq

# Create a rectangular profile in the UV plane
# The profile is a 19mm x 19mm square centered at the origin of the UV plane
# The UV coordinates from the design plan are:
#   u range: [-58.27820137826746, -56.37820137826746]  -> width = 1.9? Wait, let's compute:
#   Actually the profile dimensions are length_u=19.0, width_v=19.0
#   The UV coordinates given: start_uv = [-58.2782, -12.0401], end_uv = [-58.2782, -13.9401] etc.
#   These define a rectangle of size 1.9 x 1.9? That doesn't match 19mm.
#   Let's re-examine: The design plan says dimensions: length_u=19.0, width_v=19.0
#   But the UV coordinates span from -58.278 to -56.378 (delta=1.9) and -12.04 to -13.94 (delta=1.9)
#   This is likely because the original was in cm and converted to mm (x10), but the UV coords weren't scaled?
#   Actually the compiler notes say "unit_conversion_applied: cm_to_mm (x10)"
#   So the dimensions are 19mm, but the UV coordinates might be in the original units?
#   Let's just use the explicit dimensions: 19mm x 19mm rectangle, centered at origin of UV plane.
#   The extrude is 200mm in the +w direction.

# Define the rectangle size from explicit dimensions
length_u = 19.0  # mm
width_v = 19.0   # mm
extrude_distance = 200.0  # mm

# Create the rectangle profile centered at origin in the UV plane
# The frame has: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So we create a rectangle in the XZ plane (since u=X, v=-Z) and extrude along Y (w direction)

# Create a workplane on the XZ plane (normal is Y)
result = (cq.Workplane("XZ")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_distance))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
