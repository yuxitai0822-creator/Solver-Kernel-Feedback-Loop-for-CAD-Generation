import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 307.848 mm and width_v = 19.05 mm
# Extrude distance = 12.7 mm in the +w direction

# Define the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(307.848, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0005\\neg_03/generated.step")
