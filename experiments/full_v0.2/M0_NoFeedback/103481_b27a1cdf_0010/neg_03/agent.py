import cadquery as cq

# Create a rectangular prism with dimensions 101.6mm x 101.6mm x 38.1mm
# The profile is centered at origin, extruded in +w direction

# Create the rectangle profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103481_b27a1cdf_0010\\neg_03/generated.step")
