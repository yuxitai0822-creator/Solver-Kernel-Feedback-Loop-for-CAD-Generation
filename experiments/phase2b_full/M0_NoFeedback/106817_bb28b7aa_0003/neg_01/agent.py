import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane but we place circle at origin)
#   extrude distance = 12.192 mm
# The profile center_uv is [50.800002, 63.500002] but that is in the sketch coordinate system.
# Since the part is a simple disk, we create a circle at the origin and extrude.

# Create a circle at origin with radius 4.7117 mm
result = cq.Workplane("XY").circle(4.7117).extrude(12.192)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0003\\neg_01/generated.step")
