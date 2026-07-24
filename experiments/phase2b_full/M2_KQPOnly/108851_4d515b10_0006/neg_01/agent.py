import cadquery as cq

# Create a rectangular prism with dimensions:
# length_u = 95.25 mm (along X)
# width_v = 19.05 mm (along Z, based on frame v_dir = [0,0,-1])
# extrude_distance = 12.7 mm (along Y, based on frame w_dir = [0,1,0])

# The frame defines:
# u_dir = [1,0,0] -> X axis
# v_dir = [0,0,-1] -> negative Z axis (we'll use positive Z for simplicity, same shape)
# w_dir = [0,1,0] -> Y axis
# Extrude direction is +w, so along +Y

# Build the rectangle on the XZ plane (u,v plane) and extrude along Y
result = (
    cq.Workplane("XZ")
    .rect(95.25, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0006\\neg_01/generated.step")
