import cadquery as cq

# Design Plan: extruded circle (disk) with radius 25.4 mm and height 8.89 mm
# The circle center is at (16.994661, 17.998557) in the sketch plane (xy-plane).
# Since the coordinate system is part-local with origin at bbox min corner,
# we place the circle at that center and extrude along +z.

# Create the circle profile
circle = cq.Workplane("XY").center(16.994661, 17.998557).circle(25.4)

# Extrude to create the solid disk
disk = circle.extrude(8.89)

# Export the result
cq.exporters.export(disk, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103284_e25015aa_0003\\ex2/generated.step")
