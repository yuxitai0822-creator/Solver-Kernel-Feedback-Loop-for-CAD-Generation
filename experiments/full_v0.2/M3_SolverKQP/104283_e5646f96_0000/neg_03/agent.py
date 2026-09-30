import cadquery as cq

# Design Plan: extruded circle (disk/shaft)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which maps to world X axis per frame)
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So in CadQuery: workplane on XY, then transform to align with frame

# Build the circle on a workplane oriented to match the frame
# The frame's u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# We can create a workplane with normal = w_dir = (1,0,0) and then sketch on it
# But easier: create a workplane on the XY plane, then rotate to align

# Approach: create a workplane with normal along X axis (w_dir)
# The sketch plane will have u = (0,0,-1) and v = (0,1,0)
# Center in UV coordinates: (-15.0, 10.0) -> in 3D: center = u_dir * (-15) + v_dir * 10 = (0,0,15) + (0,10,0) = (0,10,15)
# But we need to place the circle center at that point in the workplane

# Alternative: use workplane on XZ or XY and transform
# Let's use workplane on YZ plane (normal = X axis) and then offset

result = (
    cq.Workplane("YZ")
    .center(10.0, 15.0)  # v=10, u=-15 -> in YZ plane: Y=v=10, Z=-u=15
    .circle(12.5)
    .extrude(75.0)  # extrude along X (normal of YZ plane)
)

# The extrusion direction is +X which matches +w direction
# The resulting cylinder should have span_u=25, span_v=25, span_w=75

import cadquery as cq
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\104283_e5646f96_0000\neg_03/generated.step")