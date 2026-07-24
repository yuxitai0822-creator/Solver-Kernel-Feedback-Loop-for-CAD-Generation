import cadquery as cq

# Design Plan: extruded circle (disk)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which is world X axis)
# Frame: u = (0,0,-1), v = (0,1,0), w = (1,0,0)
# So the circle lies in the YZ plane (u-v plane) and extrudes along X.

# Create the circle profile on the YZ plane (workplane origin at (0,0,0))
# Center in UV: u=-1.5, v=1.0  (but dimensions say radius=12.5, center_uv=[-15.0, 10.0])
# The dimensions block overrides the profile curves center_uv? 
# The profile curves center_uv = [-1.5, 1.0] but dimensions say center_uv = [-15.0, 10.0].
# The dimensions block is the authoritative source for explicit dimensions.
# So we use radius=12.5, center at (-15.0, 10.0) in UV coordinates.
# UV plane: u = (0,0,-1), v = (0,1,0). So u maps to -Z, v maps to +Y.
# Center in world: u*center_u + v*center_v = (0,0,-1)*(-15) + (0,1,0)*10 = (0, 10, 15)
# Wait: (0,0,-1)*(-15) = (0,0,15). So center = (0, 10, 15).

# Workplane: we can use a workplane on the YZ plane (X=0) and then offset.
# But easier: build a circle at the correct location and extrude along X.

# Use a workplane on the YZ plane (front plane in cq)
result = (
    cq.Workplane("YZ")
    .center(10.0, 15.0)  # center in YZ: Y=10, Z=15
    .circle(12.5)
    .extrude(75.0)  # extrude along X (positive direction)
)

# The extrusion direction is +w = (1,0,0) which is +X.
# The circle is at Y=10, Z=15, radius 12.5, extruded 75 mm along X.
# This matches the design plan.

import cadquery as cq
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104283_e5646f96_0000\\neg_02/generated.step")