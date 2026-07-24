import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 279.4 mm, Width (v) = 215.9 mm, Extrude distance (w) = 1.5875 mm
# Note: The design plan coordinates are in mm, but the unit_conversion_applied note says cm_to_mm (x10).
# The values in the plan are already in mm (279.4, 215.9, 1.5875), so we use them directly.

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100877_ac1e5a17_0001\\neg_02/generated.step")
