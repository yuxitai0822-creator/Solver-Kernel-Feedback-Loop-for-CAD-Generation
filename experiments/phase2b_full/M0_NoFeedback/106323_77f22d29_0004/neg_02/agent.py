import cadquery as cq

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10 mm (symmetric)

# Create the outer circle (radius 17.5 mm)
outer_circle = cq.Workplane("XY").circle(17.5)

# Create the inner circle (radius 12.5 mm) as a hole
inner_circle = cq.Workplane("XY").circle(12.5)

# Build the annulus by extruding the outer circle and cutting the inner circle
# Extrude symmetrically by total distance 10 mm (5 mm each side)
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer boundary
    .circle(12.5)  # inner boundary (hole)
    .extrude(5.0, both=True)  # symmetric extrusion: total height = 10 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106323_77f22d29_0004\\neg_02/generated.step")
