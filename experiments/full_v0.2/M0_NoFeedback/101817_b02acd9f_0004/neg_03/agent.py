import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The profile is defined in the UV plane, where:
#   u_dir = (1,0,0) -> X axis
#   v_dir = (0,0,-1) -> negative Z axis
#   w_dir = (0,1,0) -> Y axis (extrude direction)
#
# The rectangle corners in UV coordinates:
#   (7.82976, -66.34402) to (127.82976, -6.34402)
# These are small offsets; the actual dimensions are 1200mm x 600mm.
# We'll create a rectangle centered at origin with the correct spans.

# Define dimensions
length_u = 1200.0  # along X
width_v = 600.0    # along Z (negative direction)
extrude_dist = 20.0  # along Y

# Create the rectangle profile on the XY plane (Z=0), then extrude along Y
# The UV frame: u=X, v=-Z, w=Y
# So we work in the XY plane for the sketch, then extrude in Y direction.

result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0004\\neg_03/generated.step")
