import cadquery as cq

# Design Plan: Tail Stock Lever - a disk (extruded circle)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# The profile center is at (8.077681, 8.284339) in UV, but since we work in part-local
# coordinates and the part is a simple disk, we center the circle at the origin.

# Create the circular profile
circle = cq.Workplane("XY").circle(11.938)

# Extrude to create the solid disk
disk = circle.extrude(12.7)

# The result is the final part
result = disk

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0004\\neg_02/generated.step")
