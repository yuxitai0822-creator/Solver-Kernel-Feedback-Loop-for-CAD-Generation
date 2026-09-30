import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102295_86f842dd_0000\neg_01\iter_02/generated.step"

# Design parameters from the design plan:
# Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
# Extrude distance = 4.0 mm (one side, +w direction)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch is in the XZ plane (u=x, v=z), extrude along y (w)

straight_length = 28.0
radius = 10.0
extrude_distance = 4.0

# Build the stadium profile in the XZ plane (Workplane "XZ")
# The stadium consists of:
# - Left arc centered at (radius, 0) with radius, from angle 0 to 180 (top to bottom)
# - Bottom line from (radius, -radius) to (radius + straight_length, -radius)
# - Right arc centered at (radius + straight_length, 0) with radius, from angle 0 to 180 (bottom to top)
# - Top line from (radius + straight_length, radius) to (radius, radius)

# Start with a workplane in XZ
wp = cq.Workplane("XZ")

# Build the stadium profile using polyline and arc segments
# We'll construct the wire manually for precision

# Points for the stadium:
left_center = (radius, 0.0)
right_center = (radius + straight_length, 0.0)

# Build the profile as a closed wire
# Start at top of left arc: (radius, radius)
# Go to bottom of left arc via arc (center at left_center, from 90 deg to -90 deg in math coords)
# Then line to bottom of right arc
# Then arc up to top of right arc
# Then line back to start

# Using cadquery's polyline with arc approximation for reliability
# We'll discretize arcs into small line segments

N_ARC = 64  # segments per arc

# Build the outer wire
wire_points = []

# Left arc: from angle 90° (top) to -90° (bottom) going clockwise
# In our coordinate system: u=x, v=z
# Center at (radius, 0), radius = radius
# Start at (radius + radius*cos(90°), 0 + radius*sin(90°)) = (radius, radius)
# End at (radius + radius*cos(-90°), 0 + radius*sin(-90°)) = (radius, -radius)
for k in range(N_ARC + 1):
    angle_deg = 90.0 - (180.0 * k / N_ARC)  # from 90 to -90
    angle_rad = math.radians(angle_deg)
    px = left_center[0] + radius * math.cos(angle_rad)
    pz = left_center[1] + radius * math.sin(angle_rad)
    wire_points.append((px, pz))

# Bottom line: from (radius, -radius) to (radius + straight_length, -radius)
# Already at (radius, -radius) from last arc point, so just add end point
wire_points.append((radius + straight_length, -radius))

# Right arc: from angle -90° (bottom) to 90° (top) going counter-clockwise
# Center at (radius + straight_length, 0), radius = radius
# Start at (radius + straight_length + radius*cos(-90°), 0 + radius*sin(-90°)) = (radius + straight_length, -radius)
# End at (radius + straight_length + radius*cos(90°), 0 + radius*sin(90°)) = (radius + straight_length, radius)
for k in range(1, N_ARC + 1):  # skip first point (already at bottom)
    angle_deg = -90.0 + (180.0 * k / N_ARC)  # from -90 to 90
    angle_rad = math.radians(angle_deg)
    px = right_center[0] + radius * math.cos(angle_rad)
    pz = right_center[1] + radius * math.sin(angle_rad)
    wire_points.append((px, pz))

# Top line: from (radius + straight_length, radius) to (radius, radius)
# Already at (radius + straight_length, radius), so add end point
wire_points.append((radius, radius))

# Now build the wire using polyline
# Start by moving to first point, then lineTo for all subsequent points
wp = wp.moveTo(wire_points[0][0], wire_points[0][1])
for pt in wire_points[1:]:
    wp = wp.lineTo(pt[0], pt[1])
wp = wp.close()

# Extrude along the w direction (y-axis) by extrude_distance
# Since w_dir = [0,1,0], extrude along positive y
result = wp.extrude(extrude_distance)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)