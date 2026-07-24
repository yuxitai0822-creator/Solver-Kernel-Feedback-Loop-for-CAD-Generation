import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(6.0)

# Create the inner circle (hole) by subtracting
result = (
    cq.Workplane("XY")
    .circle(6.0)  # outer radius
    .circle(4.25)  # inner radius
    .extrude(12.0)  # extrude along +Z
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102410_f9877a7b_0012\\neg_03/generated.step")
