import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer radius = 3.49 mm, inner radius = 2.0 mm, thickness = 0.36 mm

# Create the washer by extruding an annulus (circle with a hole)
# Start with a cylinder for the outer shape
outer_cylinder = cq.Workplane("XY").circle(3.49).extrude(0.36)

# Create a cylinder for the inner hole
inner_cylinder = cq.Workplane("XY").circle(2.0).extrude(0.36)

# Subtract the inner cylinder from the outer cylinder to create the washer
result = outer_cylinder.cut(inner_cylinder)

# Export the result to STEP file
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107055_0500fdd1_0027\\ex2/generated.step")
