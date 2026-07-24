import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of 27.94 mm x 5.08 mm (in UV plane)
# But the dimensions table says length_u = 279.4 mm and width_v = 50.8 mm
# The profile curves show 27.94 x 5.08, which appears to be a scaling factor of 10x
# Using the explicit dimensions from the table: 279.4 mm x 50.8 mm
# Extrude distance: 19.05 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0007\\ex2/generated.step")
