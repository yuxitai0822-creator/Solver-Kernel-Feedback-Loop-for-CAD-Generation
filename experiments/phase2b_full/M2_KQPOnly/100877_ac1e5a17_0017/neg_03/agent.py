import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 254.0 mm, Width (v) = 190.5 mm, Extrude distance (w) = 3.175 mm
# Note: The design plan profiles use uv coordinates that are 1/10 of the actual dimensions
# because the plan states cm_to_mm (x10) conversion was applied.
# The profile curves show: 0-25.4 in u, 0-19.05 in v, which when multiplied by 10 give 254 and 190.5.
# So we build the rectangle directly with the full mm dimensions.

result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100877_ac1e5a17_0017\\neg_03/generated.step")
