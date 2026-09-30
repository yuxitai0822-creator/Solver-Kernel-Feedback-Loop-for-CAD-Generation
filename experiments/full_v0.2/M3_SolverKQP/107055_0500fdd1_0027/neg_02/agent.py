import cadquery as cq

# Create a washer (extruded annulus) based on the design plan.
# Outer radius: 3.49 mm, Inner radius: 2.0 mm, Thickness: 0.36 mm

# Build the outer circle
outer_circle = cq.Workplane("XY").circle(3.49)

# Cut the inner circle to create an annulus
result = outer_circle.circle(2.0).extrude(0.36)

# Export the result to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107055_0500fdd1_0027\\neg_02/generated.step")
