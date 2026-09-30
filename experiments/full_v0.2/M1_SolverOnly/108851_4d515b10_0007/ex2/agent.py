import cadquery as cq

# Create a rectangular profile in the XY plane
# Dimensions from design plan: length_u = 279.4 mm, width_v = 50.8 mm
# The profile is defined in UV space where U corresponds to X and V corresponds to Z (since w_dir = Y)
# But for simplicity, we create the rectangle in XY plane and extrude along Z

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(279.4, 50.8)
    .extrude(19.05)  # extrude distance along Z
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0007\\ex2/generated.step")
