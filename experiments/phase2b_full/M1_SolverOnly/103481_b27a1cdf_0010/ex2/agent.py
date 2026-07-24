import cadquery as cq

# Design Plan: rectangular prism with dimensions 101.6 x 101.6 x 38.1 mm
# The profile is a rectangle centered at origin, with half-width = 50.8 mm
# Extrude in +w direction (z-axis) by 38.1 mm

# Create the rectangular profile
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103481_b27a1cdf_0010\\ex2/generated.step")
