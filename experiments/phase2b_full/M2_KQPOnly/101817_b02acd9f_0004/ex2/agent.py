import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The profile is defined in the UV plane where:
#   u_dir = (1,0,0) -> X axis
#   v_dir = (0,0,-1) -> negative Z axis
#   w_dir = (0,1,0) -> Y axis (extrude direction)
#
# The rectangle corners in UV space:
#   (7.83, -66.34) to (127.83, -6.34)
# But the actual dimensions are length_u=1200, width_v=600.
# The UV coordinates given are scaled/offset from the actual dimensions.
# We'll construct the rectangle centered at origin with the correct dimensions.

# Create the rectangle profile on the XY plane (since u_dir=X, v_dir=-Z, w_dir=Y)
# We'll work in the XY plane and extrude along Y

# Rectangle dimensions
length_u = 1200.0  # along X
width_v = 600.0    # along Z (negative direction in v_dir)
extrude_dist = 20.0  # along Y

# Create the base rectangle centered at origin on XY plane
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0004\\ex2/generated.step")
