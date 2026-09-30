import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 6.0 mm, inner radius = 4.25 mm, extrude distance = 12.0 mm
# The annulus is centered at (0,0) in the sketch plane, extruded along +Z.

# Create the outer circle
outer = cq.Workplane("XY").circle(6.0)

# Create the inner circle (hole) by subtracting
result = outer.circle(4.25).extrude(12.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102410_f9877a7b_0012\\neg_03/generated.step")
