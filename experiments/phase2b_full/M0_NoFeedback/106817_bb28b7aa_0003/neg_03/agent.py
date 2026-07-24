import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane)
#   extrude distance = 12.192 mm
# The profile center_uv is given as [50.800002, 63.500002] but that is in the sketch plane;
# we place the circle at the origin in the XY plane for simplicity, then extrude along Z.

radius = 4.7117
height = 12.192

# Build the disk: circle extruded
result = cq.Workplane("XY").circle(radius).extrude(height)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0003\\neg_03/generated.step")
