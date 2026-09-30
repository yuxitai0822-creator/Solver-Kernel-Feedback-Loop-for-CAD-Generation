import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0000\neg_02\iter_00\generated.step"

# Design Plan parameters (converted from cm to mm where needed)
# Profile: circle with center at (-15.0, 10.0) and radius 12.5 mm
# Extrude: 75.0 mm along +w direction (which is +X in world frame)
# The frame has u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So w_dir is +X axis, meaning extrusion is along +X

# Create workplane on YZ plane (since extrusion is along X)
# The profile is defined in UV coordinates where U corresponds to -Z and V corresponds to +Y
# So we need to map: U -> -Z, V -> +Y
# Center in UV: (-15.0, 10.0) maps to world: Z = -(-15.0) = 15.0, Y = 10.0
# But wait - the frame says u_dir = [0,0,-1] meaning U axis points in -Z direction
# So a point at U coordinate u has world position: origin + u * u_dir + v * v_dir
# Since origin is at bbox_min_corner, we need to be careful.
# For simplicity, we'll create the circle on YZ plane centered at (10.0, 15.0) in (Y, Z)
# and extrude along +X

# Create workplane on YZ plane
wp = cq.Workplane("YZ")

# Create circle at center (Y=10.0, Z=15.0) with radius 12.5 mm
# Note: In YZ plane, the coordinates are (Y, Z)
circle = wp.center(10.0, 15.0).circle(12.5)

# Extrude along +X direction (which is the normal of YZ plane) by 75.0 mm
result = circle.extrude(75.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
