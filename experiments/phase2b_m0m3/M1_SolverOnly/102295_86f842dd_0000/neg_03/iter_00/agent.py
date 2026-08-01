import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102295_86f842dd_0000\neg_03\iter_00/generated.step"

# Design parameters from the design plan:
# Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
# Extrude distance = 4.0 mm in +w direction (which is +Y in world frame)
# The profile lies in the XZ plane (u=x, v=z, w=y)
# Stadium center: the straight segments run along u (x) from u=1.0 to u=3.8 (in UV coords)
# But the dimensions say straight_length=28.0, radius=10.0, so we need to scale.
# The UV coordinates in the plan are normalized? Actually the plan says:
#   straight_length = 28.0 mm, radius = 10.0 mm
# The UV curves show center_uv at (1.0, 0.0) and (3.8, 0.0) with radius 1.0.
# This suggests the UV coords are in some normalized space. We'll use the explicit dimensions.
# So: radius = 10.0 mm, straight_length = 28.0 mm.
# The stadium consists of two semicircles (radius 10) connected by two lines of length 28.
# Total width = 28 + 2*10 = 48 mm along u (x).
# Total height = 2*10 = 20 mm along v (z).
# The profile is centered such that the straight segments are symmetric about v=0.
# Let's place the center of the left semicircle at (0, 0) and right at (28, 0) in the sketch plane.
# But the plan's UV coords suggest left center at (1.0, 0.0) and right at (3.8, 0.0) with radius 1.0.
# That would give straight_length = 2.8 in UV space. Scaling factor = 28/2.8 = 10.
# So we can just use the explicit dimensions directly.

radius = 10.0
straight_length = 28.0
extrude_distance = 4.0

# Build the stadium profile on the XZ plane (Workplane "XZ")
# We'll construct it manually using lines and arcs.
# Left semicircle: center at (0, 0), radius 10, from angle 90 to -90 (top to bottom)
# Right semicircle: center at (straight_length, 0), radius 10, from angle -90 to 90
# Top line: from left top (0, 10) to right top (28, 10)
# Bottom line: from right bottom (28, -10) to left bottom (0, -10)

wp = cq.Workplane("XZ")

# Start at left top: (0, 10)
wp = wp.moveTo(0, 10)
# Arc from left top to left bottom (clockwise, center at (0,0), radius 10)
wp = wp.threePointArc((10, 0), (0, -10))
# Line to right bottom
wp = wp.lineTo(straight_length, -10)
# Arc from right bottom to right top (counterclockwise, center at (28,0), radius 10)
wp = wp.threePointArc((straight_length + 10, 0), (straight_length, 10))
# Line back to left top
wp = wp.lineTo(0, 10)
wp = wp.close()

# Extrude along Y (the normal of XZ plane) by extrude_distance
result = wp.extrude(extrude_distance)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
