import cadquery as cq

# Design Plan: SoapCutterLeg1 v1
# Dimensions from plan:
#   rectangle: length_u = 209.55 mm, width_v = 57.912 mm
#   extrude distance (w direction) = 19.05 mm
# Note: The plan's frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
#   This means: u = X, v = -Z, w = Y
#   So rectangle in XZ plane (with v reversed), extrude along Y.
#   We'll build a rectangle on the XZ plane, then extrude in +Y.

# Create the rectangle profile on the XZ plane (v is -Z, so width_v is along Z but reversed sign)
# Start at origin, go +X for length_u, then -Z for width_v (since v_dir = (0,0,-1))
# The profile curves in UV space:
#   start_uv (0, 5.7912) -> (0,0)  (v direction, negative)
#   (0,0) -> (20.955, 0)  (u direction, positive)
#   (20.955, 0) -> (20.955, 5.7912) (v direction, positive)
#   (20.955, 5.7912) -> (0, 5.7912) (u direction, negative)
# Note: The UV values are in cm? Actually plan says unit_conversion_applied: cm_to_mm (x10)
#   So the raw values 20.955 and 5.7912 are in cm, multiply by 10 to get mm:
#   length_u = 209.55 mm, width_v = 57.912 mm
#   But the profile curves show 20.955 and 5.7912 — these are already in mm after conversion?
#   The dimensions section says length_u = 209.55, width_v = 57.912.
#   The profile curves show start_uv (0, 5.791200000000001) and end_uv (20.955, 0).
#   This is inconsistent: 5.7912 vs 57.912, 20.955 vs 209.55.
#   The compiler note says cm_to_mm (x10), so the raw values are in cm, multiply by 10:
#   20.955 cm = 209.55 mm, 5.7912 cm = 57.912 mm.  So the profile curves are in cm.
#   We'll use the explicit dimensions: length_u = 209.55, width_v = 57.912.

length_u = 209.55  # mm, along X
width_v = 57.912   # mm, along Z (but v_dir is -Z, so we'll use positive Z and handle direction)
extrude_dist = 19.05  # mm, along Y

# Build the rectangle in the XZ plane (Y=0)
# The rectangle corners: (0,0,0), (length_u,0,0), (length_u,0,-width_v), (0,0,-width_v)
# But v_dir = (0,0,-1), so the width goes in -Z direction.
# We'll create the rectangle with positive Z and then maybe reverse? 
# Actually simpler: just create a rectangle on the XZ plane with the given dimensions.
# The exact orientation: u_dir = X, v_dir = -Z, so the rectangle lies in the X-Z plane
# with v going negative Z.  We'll create the rectangle in the XZ plane with width along Z.

result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v, centered=False)
    .extrude(extrude_dist)
)

# The above creates a rectangle in XZ plane, extruded in Y (positive Y by default).
# But the rect() function creates a rectangle centered at the origin by default.
# We used centered=False, so the rectangle starts at the current point (origin) and goes
# in the positive X and positive Z directions.  This matches the plan's frame:
#   u_dir = X, v_dir = -Z, so the rectangle should extend in +X and -Z.
# Our rect() with centered=False goes +X and +Z, which is opposite in Z.
# To match exactly, we can either:
#   1. Use centered=False and then mirror/rotate, or
#   2. Build the rectangle manually with a polyline.
# Let's build it manually to be precise.

# Manual construction:
# Points in XY plane? No, we want XZ plane.  Workplane("XZ") gives us XY? 
# Actually cq.Workplane("XZ") sets the plane normal to Y, so the workplane is XZ.
# The .rect() on that plane draws in X and Z directions.
# With centered=False, the rectangle starts at (0,0) and goes to (length_u, width_v) in the plane coordinates.
# In the XZ plane, plane coordinates are (X, Z).  So it goes from (0,0) to (length_u, width_v) in XZ.
# But we want it to go from (0,0) to (length_u, -width_v) in XZ (since v_dir = -Z).
# So we need to negate the Z dimension.

# Alternative: use a polyline to trace the exact path.
# The profile in UV space:
#   (0, 5.7912) -> (0, 0)  : v direction, negative
#   (0, 0) -> (20.955, 0)  : u direction, positive
#   (20.955, 0) -> (20.955, 5.7912) : v direction, positive
#   (20.955, 5.7912) -> (0, 5.7912) : u direction, negative
# In mm: multiply by 10: 209.55 and 57.912
# In 3D space (u=X, v=-Z):
#   (0, 0, -57.912) -> (0, 0, 0)  : v direction (negative Z to zero)
#   (0, 0, 0) -> (209.55, 0, 0)  : u direction (positive X)
#   (209.55, 0, 0) -> (209.55, 0, -57.912) : v direction (zero to negative Z)
#   (209.55, 0, -57.912) -> (0, 0, -57.912) : u direction (negative X)

pts = [
    (0, 0, -width_v),   # start: (0, 0, -57.912)
    (0, 0, 0),          # (0, 0, 0)
    (length_u, 0, 0),   # (209.55, 0, 0)
    (length_u, 0, -width_v),  # (209.55, 0, -57.912)
]

result = (
    cq.Workplane("XZ")
    .polyline(pts)
    .close()
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
