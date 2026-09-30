import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 12.7 mm, Inner radius = 7.965948 mm, Extrude distance = 101.6 mm

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(12.7)

# Create the inner circle (hole) by subtracting from the outer circle
# Using the same center (0,0)
result = (
    cq.Workplane("XY")
    .circle(12.7)  # outer radius
    .circle(7.965948)  # inner radius (hole)
    .extrude(101.6)  # extrude along +Z
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102314_91648bfc_0000\\neg_03/generated.step")
