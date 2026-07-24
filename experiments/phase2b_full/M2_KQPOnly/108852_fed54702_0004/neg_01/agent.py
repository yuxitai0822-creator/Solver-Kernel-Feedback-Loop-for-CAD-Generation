import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle of radius 0.396875 for the profile ring,
# but the dimensions section says radius = 3.96875. The dimensions section is the
# authoritative source for the actual part dimensions. The ring radius 0.396875
# appears to be a different measurement (possibly thread root radius).
# We use the dimensions radius = 3.96875 as the main cylinder radius.

# Create the cylinder by extruding a circle
result = cq.Workplane("XY").circle(3.96875).extrude(139.7)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108852_fed54702_0004\\neg_01/generated.step")
