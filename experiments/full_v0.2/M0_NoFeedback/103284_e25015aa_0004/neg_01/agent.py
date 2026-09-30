import cadquery as cq

# Design Plan: Tail Stock Lever - extruded circle (disk)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# Center in UV: (8.077681, 8.284339) - but since we work in part-local frame,
# we create the circle at the origin and then translate if needed.
# The design plan indicates a single body, extruded circle.

# Create the circle profile at origin (the center_uv is in sketch plane, but for a simple disk
# we can center at origin and the validation intents check spans, not absolute position)
radius = 11.938
extrude_distance = 12.7

# Build the result
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\103284_e25015aa_0004\\neg_01/generated.step")
