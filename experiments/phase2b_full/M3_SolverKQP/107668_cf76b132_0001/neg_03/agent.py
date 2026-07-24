import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 132.5 mm, inner radius = 75.0 mm, extrude distance = 100.0 mm
# Note: The design plan indicates unit conversion from cm to mm (x10), so radii are 13.25 cm -> 132.5 mm, 7.5 cm -> 75.0 mm, extrude 10 cm -> 100.0 mm

# Create the outer circle (radius 132.5 mm)
outer_circle = cq.Workplane("XY").circle(132.5)

# Create the inner circle (radius 75.0 mm) as a hole
result = outer_circle.circle(75.0).extrude(100.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107668_cf76b132_0001\\neg_03/generated.step")
