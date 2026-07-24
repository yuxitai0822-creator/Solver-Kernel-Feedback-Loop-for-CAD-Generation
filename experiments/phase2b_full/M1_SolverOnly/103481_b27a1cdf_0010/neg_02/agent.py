import cadquery as cq

# Design Plan: rectangular prism with dimensions 101.6 x 101.6 x 38.1 mm
# The profile is a rectangle centered at origin with half-side = 5.08 (since start_uv = +/-5.08)
# Extrude distance = 38.1 mm in +w direction

# Create the rectangular profile
profile = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(101.6, 101.6)
)

# Extrude to create the solid
result = profile.extrude(38.1)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103481_b27a1cdf_0010\\neg_02/generated.step")
