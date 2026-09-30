import cadquery as cq

# Design Plan: Washer (2) - extruded annulus
# Dimensions: outer radius = 3.49 mm, inner radius = 2.0 mm, thickness = 0.36 mm

# Create the outer circle
outer_circle = cq.Workplane("XY").circle(3.49)

# Create the inner circle (hole) by subtracting
result = outer_circle.circle(2.0).extrude(0.36)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\107055_0500fdd1_0027\\neg_03/generated.step")
