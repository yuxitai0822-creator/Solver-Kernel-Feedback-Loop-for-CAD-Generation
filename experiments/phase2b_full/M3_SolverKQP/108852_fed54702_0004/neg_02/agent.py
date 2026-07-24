import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a disk (extruded circle) with radius 0.396875 in the profile curves
# but the dimensions section says radius = 3.96875. The compiler notes mention cm_to_mm conversion (x10).
# The profile curve radius 0.396875 * 10 = 3.96875, so we use the dimension value 3.96875 mm.

radius = 3.96875  # mm
height = 139.7    # mm

# Create the disk by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108852_fed54702_0004\\neg_02/generated.step")
