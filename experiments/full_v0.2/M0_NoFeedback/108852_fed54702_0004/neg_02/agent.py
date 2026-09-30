import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle profile with radius 0.396875 in the profile curves,
# but the dimensions section gives radius = 3.96875. The dimensions section is authoritative.
# The profile curves radius (0.396875) appears to be a different value (possibly a different feature),
# but the overall part is a disk with radius 3.96875 and height 139.7.

# Create the circle profile
result = cq.Workplane("XY").circle(3.96875).extrude(139.7)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108852_fed54702_0004\\neg_02/generated.step")
