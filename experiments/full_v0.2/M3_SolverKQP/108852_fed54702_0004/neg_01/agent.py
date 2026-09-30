import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle of radius 0.396875 in the profile curves,
# but the dimensions section gives radius = 3.96875. The dimensions section is authoritative.
# The profile curve radius 0.396875 appears to be a unit conversion artifact (cm vs mm).
# We use the explicit dimension radius = 3.96875 mm.

# Create the circle profile
result = (
    cq.Workplane("XY")
    .circle(3.96875)  # radius in mm
    .extrude(139.7)    # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108852_fed54702_0004\\neg_01/generated.step")
