import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle profile extruded along the w direction.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# This means the extrusion is along the y-axis (world), and the circle lies in the xz-plane.
# We'll create the circle on the xz-plane and extrude along y.

# Create the circle profile on the xz-plane (normal = y-axis)
result = (
    cq.Workplane("XZ")
    .circle(3.96875)  # radius in mm
    .extrude(139.7)   # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108852_fed54702_0004\\neg_01/generated.step")
