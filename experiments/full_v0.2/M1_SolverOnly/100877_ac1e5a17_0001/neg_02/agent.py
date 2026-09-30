import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 279.4 mm, Width (v) = 215.9 mm, Extrude distance (w) = 1.5875 mm

# Note: The design plan uses a coordinate system where:
# - u corresponds to x-axis
# - v corresponds to y-axis
# - w corresponds to z-axis
# The origin is at the minimum corner of the bounding box

# Create the rectangle profile on the xy-plane
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100877_ac1e5a17_0001\\neg_02/generated.step")
