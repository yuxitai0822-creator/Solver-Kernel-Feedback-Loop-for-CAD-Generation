import cadquery as cq

# Design Plan: Tail Stock Lever - extruded circle (disk)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# The profile center is at (8.077681, 8.284339) in UV plane, but since we are creating a new body
# we can place the circle at the origin and then translate if needed.
# However, the design plan specifies the center in UV coordinates, which likely corresponds to
# the sketch plane location. For simplicity and to match the expected span (23.876 mm diameter),
# we create the circle centered at (0,0) and extrude.

# Create a circle with radius 11.938 mm
result = cq.Workplane("XY").circle(11.938).extrude(12.7)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103284_e25015aa_0004\\ex2/generated.step")
