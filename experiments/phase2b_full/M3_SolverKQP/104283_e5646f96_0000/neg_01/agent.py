import cadquery as cq

# Design Plan: extruded circle (disk/shaft)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which maps to world X axis per frame definition)
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So in CadQuery: workplane on XY, then transform to align with frame

# Build the circle profile on a workplane oriented to the frame
# The frame's u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# We'll create a workplane with normal along w_dir (X axis) and u_dir as the X direction
# But CadQuery workplane expects normal and optionally a direction for X axis.
# Using plane with normal (1,0,0) and then rotating to align u_dir with (0,0,-1) is tricky.
# Simpler: create the circle on the YZ plane (normal X) and position center accordingly.
# The center_uv = (-15.0, 10.0) in UV coordinates where U = (0,0,-1), V = (0,1,0)
# So center in world: (-15.0)*(0,0,-1) + 10.0*(0,1,0) = (0, 10, 15)
# Then extrude along +w = (1,0,0) for 75 mm.

result = (
    cq.Workplane("YZ")
    .circle(12.5)
    .extrude(75.0)
)

# The circle is centered at origin on YZ plane; we need to move it to (0, 10, 15)
result = result.translate((0, 10, 15))

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\104283_e5646f96_0000\neg_01/generated.step")
