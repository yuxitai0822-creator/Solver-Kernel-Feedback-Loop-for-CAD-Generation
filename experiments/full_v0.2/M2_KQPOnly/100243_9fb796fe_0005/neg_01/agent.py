import cadquery as cq

# Create a rectangular profile in the UV plane
# The profile is a 19mm x 19mm square centered at the origin
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The profile vertices in UV coordinates are:
#   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
# This is a 2mm x 1.9mm rectangle in UV space, but the actual dimensions are 19mm x 19mm
# The extrude distance is 200mm along +w direction

# Create the rectangle profile
# The profile is defined by 4 points forming a rectangle
# Width along u: 19.0 mm, width along v: 19.0 mm
# Center the rectangle at the origin for simplicity

# Define the rectangle dimensions
width_u = 19.0  # along u (x-axis)
width_v = 19.0  # along v (z-axis negative)
extrude_dist = 200.0  # along w (y-axis)

# Create the rectangle centered at origin in the UV plane
# The UV plane corresponds to XZ plane in world coordinates
# u_dir = (1,0,0) -> X axis
# v_dir = (0,0,-1) -> -Z axis
# w_dir = (0,1,0) -> Y axis

# Create a rectangle centered at origin
result = (
    cq.Workplane("XZ")
    .rect(width_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100243_9fb796fe_0005\\neg_01/generated.step")
