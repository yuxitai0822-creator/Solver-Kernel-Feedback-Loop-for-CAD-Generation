import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, Total height = 10.0 mm (symmetric about XY plane)

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (hole) by subtracting from the outer circle
# We'll use a workplane approach: start with a circle, then cut the inner circle
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer radius
    .circle(12.5)  # inner radius (hole)
    .extrude(10.0 / 2, both=True)  # symmetric extrusion: total height 10.0 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106323_77f22d29_0004\\neg_02/generated.step")
