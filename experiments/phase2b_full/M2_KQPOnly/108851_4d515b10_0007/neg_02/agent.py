import cadquery as cq

# Design Plan: SoapCutterBackBar1 v1
# Dimensions: length_u = 279.4 mm, width_v = 50.8 mm, extrude_distance = 19.05 mm
# The profile is a rectangle in the UV plane, extruded along the W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = X, v = -Z, w = Y
# The rectangle in UV coordinates: start at (0, 5.08) -> (0,0) -> (27.94,0) -> (27.94,5.08) -> back to (0,5.08)
# Note: The UV coordinates given are 27.94 x 5.08, but the dimensions say length_u=279.4, width_v=50.8.
# The UV coordinates appear to be in cm (since compiler notes say cm_to_mm x10).
# 27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm. So the rectangle in mm is:
# start at (0, 50.8) -> (0,0) -> (279.4,0) -> (279.4,50.8) -> back to (0,50.8)
# This is a simple rectangle aligned with axes in UV space.
# In 3D: u -> X, v -> -Z, so the rectangle lies in the XZ plane (with v inverted).
# The extrude direction is +w = +Y, distance = 19.05 mm.

# Build the rectangle in the XY plane (since CadQuery works in XY by default), then rotate if needed.
# Simpler: create a box directly with the given dimensions.
# The rectangle spans 279.4 mm in X (u), 50.8 mm in Z (v), and extrudes 19.05 mm in Y (w).
# But careful: v_dir = (0,0,-1) means v points in -Z. So the rectangle in 3D has corners:
# (0,0,0) -> (279.4,0,0) -> (279.4,0,-50.8) -> (0,0,-50.8) in the plane Y=0.
# Then extrude in +Y direction by 19.05 mm.

result = (
    cq.Workplane("XY")
    .rect(279.4, 50.8, centered=False)
    .extrude(19.05)
)

# The above creates a box from (0,0,0) to (279.4, 19.05, 50.8) but we need the v direction to be -Z.
# Actually, rect() creates a rectangle centered at the origin by default. With centered=False, the first corner is at (0,0).
# So the rectangle goes from (0,0) to (279.4, 50.8) in the XY plane.
# Then extrude in +Z (default) by 19.05 mm.
# This gives a box from (0,0,0) to (279.4, 50.8, 19.05).
# But we need the v direction to be -Z, meaning the rectangle should be in the XZ plane with v inverted.
# To match exactly: the rectangle in UV is (0,5.08)->(0,0)->(27.94,0)->(27.94,5.08) in cm.
# In mm: (0,50.8)->(0,0)->(279.4,0)->(279.4,50.8).
# In 3D with u=X, v=-Z: points become:
# (0, 0, -50.8) -> (0, 0, 0) -> (279.4, 0, 0) -> (279.4, 0, -50.8)
# This is a rectangle in the XZ plane at Y=0, with corners as above.
# Extrude in +Y (w direction) by 19.05 mm.
# So we need to build the rectangle in the XZ plane and extrude in Y.

# Let's do it properly:
result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8, centered=False)
    .extrude(19.05)
)

# Check: Workplane("XZ") means the plane is XZ, so rect() draws in XZ plane.
# With centered=False, the first corner is at (0,0) in the plane coordinates.
# In the XZ plane, (0,0) corresponds to (0,0,0) in 3D.
# The rectangle goes from (0,0) to (279.4, 50.8) in plane coordinates.
# In 3D, that's from (0,0,0) to (279.4, 0, 50.8).
# But we need the v direction to be -Z, so the rectangle should go from (0,0,0) to (279.4, 0, -50.8).
# To achieve this, we can either mirror or use a negative dimension.
# Using rect(279.4, -50.8, centered=False) will flip the v direction.

result = (
    cq.Workplane("XZ")
    .rect(279.4, -50.8, centered=False)
    .extrude(19.05)
)

# Now the rectangle in XZ plane: first corner at (0,0,0), goes to (279.4, 0, -50.8).
# Extrude in +Y (default for Workplane("XZ") extrudes along Y) by 19.05 mm.
# This gives a box from (0,0,-50.8) to (279.4, 19.05, 0).
# This matches the expected geometry.

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108851_4d515b10_0007\neg_02/generated.step")
