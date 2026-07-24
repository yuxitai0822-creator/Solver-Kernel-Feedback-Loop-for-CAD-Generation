import cadquery as cq

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm and height 6.8707 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The circle center in UV is at (11.430000364780426, 0.0) but that is in the profile's UV space.
# The profile radius is 4.87045 mm (from dimensions).
# The extrude distance is 6.8707 mm along +w direction.
# We'll create a circle centered at (0,0) in the XY plane, then extrude along Z.
# Then we'll rotate/translate to match the specified frame.

# Step 1: Create the base circle at origin in XY plane
result = cq.Workplane("XY").circle(4.87045).extrude(6.8707)

# Step 2: Transform to match the design frame.
# The design frame has:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis
#   w_dir = (0,1,0)  -> Y axis
# So the part's local coordinate system is:
#   X' = X
#   Y' = -Z
#   Z' = Y
# This is a rotation: rotate 90 degrees about X axis, then maybe reflect?
# Actually, mapping: (X,Y,Z) -> (X, -Z, Y) is a rotation of -90 deg around X.
# Let's apply: rotate around X by -90 degrees.
result = result.rotate((0,0,0), (1,0,0), -90)

# Step 3: The profile center_uv is at (11.430000364780426, 0.0) in UV space.
# In our transformed coordinate system, U corresponds to X, V corresponds to Y (which is -Z original).
# So we need to translate by (11.430000364780426, 0, 0) in the new frame.
result = result.translate((11.430000364780426, 0, 0))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0002\\neg_02/generated.step")
