import cadquery as cq

# Design Plan: Tail Stock Lever - extruded circle (disk)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# The profile center is at (8.077681, 8.284339) in UV plane, but we place the circle at origin
# and shift the workplane accordingly.

# Create a workplane and draw a circle of radius 11.938 mm
result = (
    cq.Workplane("XY")
    .circle(11.938)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0004\\neg_01/generated.step")
