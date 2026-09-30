import cadquery as cq

# Create a rectangular plate with dimensions from design plan
# The design plan specifies a rectangle of 193.0 x 55.0 mm (in UV space)
# Note: The dimensions in the plan are given as 1930.0 and 550.0, but the profile curves show 193.0 and 55.0
# The compiler notes indicate cm_to_mm conversion (x10), so the actual dimensions are 193.0 x 55.0 mm
# Extrude distance is 50.0 mm in the +w direction

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(193.0, 55.0)
    .extrude(50.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0002\\neg_02/generated.step")
