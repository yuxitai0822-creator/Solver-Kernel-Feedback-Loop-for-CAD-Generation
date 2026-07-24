import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, Total height = 10.0 mm (symmetric extrusion)

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (hole) by subtracting
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer boundary
    .circle(12.5)  # inner boundary (cutout)
    .extrude(10.0, both=True)  # symmetric extrusion: total height 10 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106323_77f22d29_0004\\neg_03/generated.step")
