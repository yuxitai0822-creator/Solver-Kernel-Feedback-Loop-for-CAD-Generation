import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius: 12.7 mm, Inner radius: 7.965948 mm, Extrude distance: 101.6 mm

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(12.7)

# Create the inner circle (hole)
inner_circle = cq.Workplane("XY").circle(7.965948)

# Create the annulus by subtracting inner from outer
result = (
    cq.Workplane("XY")
    .circle(12.7)  # outer radius
    .circle(7.965948)  # inner radius
    .extrude(101.6)  # extrude distance
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102314_91648bfc_0000\\neg_02/generated.step")
