import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer radius = 3.49 mm, inner radius = 2.0 mm, thickness = 0.36 mm

# Create the outer circle (radius 3.49)
outer_circle = cq.Workplane("XY").circle(3.49)

# Create the inner circle (radius 2.0) and subtract to form annulus
result = cq.Workplane("XY").circle(3.49).circle(2.0).extrude(0.36)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\107055_0500fdd1_0027\\neg_02/generated.step")
