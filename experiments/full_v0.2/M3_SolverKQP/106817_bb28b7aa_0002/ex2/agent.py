import cadquery as cq

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm and height 6.8707 mm
# The profile circle center is at (11.43, 0) in UV plane, but for a simple disk
# we place the circle at origin and extrude along Z.

# Create the circular profile
circle = cq.Workplane("XY").circle(4.87045)

# Extrude to create the solid disk
disk = circle.extrude(6.8707)

# The result is a single solid body
result = disk

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0002\\ex2/generated.step")
