import cadquery as cq

# Design Plan: extruded circle (disk) with radius 3.0 mm and height 14.0 mm
# The part is a simple cylinder centered at the origin.

# Create a circle profile with radius 3.0 mm
circle = cq.Workplane("XY").circle(3.0)

# Extrude the circle along the +Z direction by 14.0 mm
result = circle.extrude(14.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\107467_a8afc51d_0000\\neg_02/generated.step")
