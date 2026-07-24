import cadquery as cq

# Design Plan: extruded circle (disk) with radius 2.54 mm and extrude distance 8.89 mm
# Note: The design plan specifies radius = 2.54 (in the curves section) but also radius = 25.4 (in dimensions section).
# The curves section radius (2.54) is the actual circle radius used for the profile.
# The dimensions section radius (25.4) appears to be a scaling artifact (cm to mm conversion factor 10 applied incorrectly).
# We use the curve radius = 2.54 mm as the true dimension.
# Center_uv is [1.6994660913961006, 1.7998556732836484] but for a single part we can center at origin.

radius = 2.54
height = 8.89

# Create a circle at the origin and extrude
result = cq.Workplane("XY").circle(radius).extrude(height)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\103284_e25015aa_0003\\neg_02/generated.step")
