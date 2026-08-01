import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: u=[-6.12, -1.88], v=[10.88, 15.12]  (span 4.24 each)
# Inner rectangle: u=[-6.0, -2.0], v=[11.0, 15.0]  (span 4.0 each)
# Extrude along w (x-axis) by 1120.0 mm
# Note: coordinates are in mm (converted from cm)

# Build the outer rectangle profile on YZ plane (u=v, w=x)
# The frame axes: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So u maps to -Z, v maps to Y, w maps to X
# We'll work on YZ plane (X=0) and extrude along X

# Outer rectangle corners in (u,v) = (z,y) space:
# (-1.88, 10.88) -> z=-1.88, y=10.88
# (-1.88, 15.12) -> z=-1.88, y=15.12
# (-6.12, 15.12) -> z=-6.12, y=15.12
# (-6.12, 10.88) -> z=-6.12, y=10.88

# Inner rectangle corners in (u,v) = (z,y) space:
# (-2.0, 11.0) -> z=-2.0, y=11.0
# (-6.0, 11.0) -> z=-6.0, y=11.0
# (-6.0, 15.0) -> z=-6.0, y=15.0
# (-2.0, 15.0) -> z=-2.0, y=15.0

# Create workplane on YZ (X=0)
wp = cq.Workplane("YZ")

# Outer rectangle: center at ((-1.88 + -6.12)/2, (10.88 + 15.12)/2) = (-4.0, 13.0)
# width = 4.24, height = 4.24
outer_center_u = (-1.88 + -6.12) / 2  # = -4.0
outer_center_v = (10.88 + 15.12) / 2  # = 13.0
outer_width = 4.24
outer_height = 4.24

# Inner rectangle: center at ((-2.0 + -6.0)/2, (11.0 + 15.0)/2) = (-4.0, 13.0)
# width = 4.0, height = 4.0
inner_center_u = (-2.0 + -6.0) / 2  # = -4.0
inner_center_v = (11.0 + 15.0) / 2  # = 13.0
inner_width = 4.0
inner_height = 4.0

# Build the profile: outer rectangle with inner hole
# First create outer rectangle
profile = wp.moveTo(outer_center_u, outer_center_v).rect(outer_width, outer_height, centered=True)

# Create inner rectangle as a separate wire for cutting
inner_wp = cq.Workplane("YZ").moveTo(inner_center_u, inner_center_v).rect(inner_width, inner_height, centered=True)

# Extrude the outer rectangle along X (positive direction) by 1120.0 mm
result = profile.extrude(1120.0)

# Cut the inner hole: extrude inner rectangle and subtract
inner_solid = inner_wp.extrude(1120.0)
result = result.cut(inner_solid)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0002\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
