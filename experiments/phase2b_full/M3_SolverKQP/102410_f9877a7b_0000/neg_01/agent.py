import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(6.0)

# Create the inner circle (hole) on the same workplane
# Using the same workplane, we can cut the inner circle
result = cq.Workplane("XY").circle(6.0).circle(4.25).extrude(11.5)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102410_f9877a7b_0000\\neg_01/generated.step")
