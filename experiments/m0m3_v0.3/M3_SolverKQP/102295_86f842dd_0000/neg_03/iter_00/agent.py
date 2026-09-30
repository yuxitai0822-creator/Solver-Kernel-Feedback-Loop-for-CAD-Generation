import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102295_86f842dd_0000\neg_03\iter_00/generated.step"

# Design parameters from the design plan
# The stadium profile has:
# - Two arcs: radius = 10.0 mm (scaled from 1.0 * 10 for cm->mm conversion)
# - Straight length = 28.0 mm (distance between arc centers)
# - Extrude distance = 4.0 mm

radius = 10.0  # mm
straight_length = 28.0  # mm
extrude_distance = 4.0  # mm

# The stadium is centered along the X-axis in the sketch plane (XZ plane)
# Arc centers at x = radius and x = radius + straight_length
# But the design plan shows centers at uv coordinates (1.0, 0.0) and (3.8, 0.0) before scaling
# After cm->mm conversion (x10): centers at (10.0, 0.0) and (38.0, 0.0)
# The straight_length = 38.0 - 10.0 = 28.0 mm (matches)

# Build the stadium profile on the XZ plane (Y is extrusion direction)
# The profile lies in the XZ plane, extruded along Y

# Start with a workplane on XZ
wp = cq.Workplane("XZ")

# Build the stadium profile using the center points
center1_x = radius  # 10.0
center2_x = radius + straight_length  # 38.0

# Create the stadium by:
# 1. Two arcs (semicircles) at each end
# 2. Two lines connecting them

# We'll build the profile as a closed wire
# Start at the bottom of the left arc: (center1_x, -radius)
# Go to bottom of right arc: (center2_x, -radius)
# Arc around right end: center at (center2_x, 0), from angle -90 to 90
# Go to top of left arc: (center1_x, radius)
# Arc around left end: center at (center1_x, 0), from angle 90 to 270

# Using the polyline+arc approach with discretization for robustness
N_ARC = 64  # segments per arc

# Build the profile points
points = []

# Start at bottom-left of left arc
# Left arc: center at (center1_x, 0), radius = radius, from angle 180 to 0 (going clockwise)
# Actually, let's trace the profile in order:
# 1. Left arc from top (angle 90) to bottom (angle -90) going clockwise
# 2. Bottom line from left to right
# 3. Right arc from bottom (angle -90) to top (angle 90) going clockwise
# 4. Top line from right to left

# Left arc: center (center1_x, 0), radius, from 90° to -90° (clockwise = decreasing angle)
for k in range(N_ARC + 1):
    angle = math.radians(90 - 180 * k / N_ARC)  # 90 to -90
    px = center1_x + radius * math.cos(angle)
    pz = radius * math.sin(angle)
    points.append((px, pz))

# Bottom line: from left arc bottom to right arc bottom
# Already at (center1_x, -radius), need to go to (center2_x, -radius)
# The last point of the arc is at angle -90: (center1_x, -radius)
# Add the bottom line end point
points.append((center2_x, -radius))

# Right arc: center (center2_x, 0), radius, from -90° to 90° (counter-clockwise = increasing angle)
for k in range(1, N_ARC + 1):  # start from 1 to avoid duplicating the start point
    angle = math.radians(-90 + 180 * k / N_ARC)  # -90 to 90
    px = center2_x + radius * math.cos(angle)
    pz = radius * math.sin(angle)
    points.append((px, pz))

# Top line: from right arc top to left arc top
# Already at (center2_x, radius), need to go to (center1_x, radius)
points.append((center1_x, radius))

# Now build the wire using polyline
# Start by moving to the first point, then lineTo for each subsequent point
wp = wp.moveTo(points[0][0], points[0][1])
for pt in points[1:]:
    wp = wp.lineTo(pt[0], pt[1])
wp = wp.close()

# Extrude along Y (positive direction)
result = wp.extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
