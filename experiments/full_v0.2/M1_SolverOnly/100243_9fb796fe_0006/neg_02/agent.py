import cadquery as cq

# Design Plan: Drone Leg - square strut
# Profile: rectangle 19mm x 19mm, extruded 130mm along w direction
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle is defined in UV space with corners at:
#   (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
# This gives a rectangle of width (u span) = 1.9 mm? Wait: -56.3782 - (-58.2782) = 1.9, but expected length_u = 19.0.
# The design plan says length_u = 19.0, width_v = 19.0. The UV coordinates seem scaled by 0.1 (cm to mm conversion factor 10? Actually note: unit_conversion_applied: cm_to_mm (x10)).
# The original source was in cm, converted to mm by x10. The UV coordinates appear to be in cm? Let's check: span in u: -56.3782 - (-58.2782) = 1.9 cm = 19 mm. Yes, that matches.
# So the rectangle in mm is: u from -58.2782 to -56.3782 (span 1.9 cm = 19 mm), v from -13.9401 to -12.0401 (span 1.9 cm = 19 mm).
# But the frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# So in world coordinates: u -> x, v -> -z, w -> y.
# The rectangle lies in the x-z plane (since u and v map to x and -z).
# Extrude direction is +w = +y, distance 130 mm.

# Build the rectangle in the x-z plane, then extrude along y.
# Center the rectangle at the midpoint of the UV coordinates for convenience.
# UV center: u_center = (-58.2782 + -56.3782)/2 = -57.3282, v_center = (-13.9401 + -12.0401)/2 = -12.9901
# In world: x_center = -57.3282, z_center = -(-12.9901) = 12.9901 (since v_dir = (0,0,-1), so world z = -v)
# But we can just build the rectangle directly using the given corners.

# Define points in UV space, then map to world:
# Point A: u=-58.2782, v=-12.0401 -> world: x=-58.2782, z=-(-12.0401)=12.0401
# Point B: u=-58.2782, v=-13.9401 -> world: x=-58.2782, z=-(-13.9401)=13.9401
# Point C: u=-56.3782, v=-13.9401 -> world: x=-56.3782, z=13.9401
# Point D: u=-56.3782, v=-12.0401 -> world: x=-56.3782, z=12.0401

# So rectangle in x-z plane: corners at (x,z): (-58.2782, 12.0401), (-58.2782, 13.9401), (-56.3782, 13.9401), (-56.3782, 12.0401)
# Width in x: 1.9 mm? Wait: -56.3782 - (-58.2782) = 1.9, but expected 19 mm. There's a factor of 10 discrepancy.
# The design plan says length_u = 19.0 mm, but the UV coordinates give 1.9. The note says "unit_conversion_applied: cm_to_mm (x10)".
# This means the original source was in cm, and the UV coordinates are in cm. So we must multiply by 10 to get mm.
# So actual rectangle in mm: x from -582.782 to -563.782 (span 19 mm), z from 120.401 to 139.401 (span 19 mm).
# Let's verify: -563.782 - (-582.782) = 19.0 mm. Yes.

# So we build the rectangle with these scaled coordinates.

# Create the rectangle in the x-z plane (y=0) and extrude along y by 130 mm.

result = (
    cq.Workplane("XZ")
    .moveTo(-582.782, 120.401)  # x, z coordinates (since workplane is XZ, first arg is x, second is z)
    .lineTo(-582.782, 139.401)
    .lineTo(-563.782, 139.401)
    .lineTo(-563.782, 120.401)
    .close()
    .extrude(130.0)  # extrude along y (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100243_9fb796fe_0006\\neg_02/generated.step")
