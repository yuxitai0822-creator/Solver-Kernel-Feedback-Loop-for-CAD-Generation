import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so positive V goes in -Z direction)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The rectangle corners in UV coordinates:
#   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# But note: the design plan dimensions show length_u = 95.25 and width_v = 571.5
# The UV coordinates given are for a smaller rectangle (9.525 x 57.15).
# This appears to be a scaling issue from cm->mm conversion (9.525*10=95.25, 57.15*10=571.5).
# So we use the actual dimensions: length_u = 95.25 mm, width_v = 571.5 mm.

# Build the rectangle in the XY plane (since u_dir = X, v_dir = -Z, we need to orient)
# Actually, let's build it directly in the XY plane and then rotate if needed.
# The frame says: u_dir = X, v_dir = -Z, w_dir = Y.
# So the profile lies in the X-Z plane (u along X, v along -Z).
# We'll create a workplane on the XZ plane, draw the rectangle, then extrude along Y.

# Create the rectangle on the XZ plane (front view in CadQuery)
# The rectangle spans from (0,0) to (95.25, 571.5) in (X, Z) but v_dir is -Z so we need to handle sign.
# Actually, v_dir = (0,0,-1) means positive V maps to negative Z.
# So the rectangle corners in XYZ:
#   (0,0,0) -> (0, 0, 0)
#   (9.525, 0, 0) -> (9.525, 0, 0) but scaled: (95.25, 0, 0)
#   (9.525, 57.15, 0) -> (95.25, 0, -571.5)
#   (0, 57.15, 0) -> (0, 0, -571.5)
# So the rectangle is in the XZ plane, with Z negative.

# Let's build it simply: workplane on XZ, centered at origin, then extrude along Y.
# But the origin is at bbox_min_corner, so we place the rectangle starting at origin.

result = (
    cq.Workplane("XZ")
    .rect(95.25, 571.5, centered=False)
    .extrude(19.05)
)

# The above places the rectangle with its corner at the origin in the XZ plane.
# However, the rect() function with centered=False places the corner at the current point.
# The default current point is (0,0,0) in the workplane's local coordinates.
# For workplane "XZ", the local coordinates are (X, Z).
# So rect(95.25, 571.5, centered=False) creates a rectangle from (0,0) to (95.25, 571.5) in XZ.
# This matches our desired shape.
# Extrude along Y (the normal of XZ plane) by 19.05 mm.

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101269_f084ba14_0023\\neg_01/generated.step")
