import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle profile extruded along the w direction.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# In CadQuery, we create a circle on the XY plane and extrude along Z.
# To match the frame orientation, we'll create the circle centered at origin
# and extrude along the positive Z axis (which corresponds to +w direction).

# Create the circle profile
circle = cq.Workplane("XY").circle(3.96875)

# Extrude along Z (positive direction) to create the disk/rod
result = circle.extrude(139.7)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108852_fed54702_0004\\neg_03/generated.step")
