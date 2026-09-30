import cadquery as cq

# Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
# The coordinate system is part-local with origin at bbox min corner.
# We create a cylinder centered at (0,0,0) and then translate so that
# the bounding box min corner is at (0,0,0).

radius = 0.8
height = 4.0

# Create a cylinder centered at origin, with axis along +Z
# The cylinder will extend from -height/2 to +height/2 along Z
result = cq.Workplane("XY").circle(radius).extrude(height)

# Now translate so that the bottom face is at z=0 (bbox min corner at origin)
# The cylinder currently spans from z=0 to z=height (since extrude from XY plane)
# That already matches bbox_min_corner convention (min corner at origin)
# No translation needed.

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102760_26430589_0037\\neg_03/generated.step")
