import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102295_86f842dd_0000\neg_03\iter_02/generated.step"

# Design parameters from the design plan
radius = 10.0  # mm
straight_length = 28.0  # mm
extrude_distance = 4.0  # mm

# Arc centers
center1_x = radius  # 10.0
center2_x = radius + straight_length  # 38.0

# Build the stadium profile on the XZ plane (Y is extrusion direction)
wp = cq.Workplane("XZ")

# Build the profile as a closed wire using proper arcs
# The stadium consists of:
# 1. Left semicircle: center at (center1_x, 0), radius, from 180° to 0° (clockwise)
# 2. Bottom line: from left arc bottom to right arc bottom
# 3. Right semicircle: center at (center2_x, 0), radius, from 0° to 180° (clockwise)
# 4. Top line: from right arc top to left arc top

# Use cadquery's built-in arc and line capabilities for a clean profile
# Start at the leftmost point of the left arc (angle 180°)
start_x = center1_x - radius  # 0.0
start_z = 0.0

# Build the profile using workplane methods
# Move to start point
wp = wp.moveTo(start_x, start_z)

# Left arc: from 180° to 0° (clockwise) - this is the left semicircle
# In cadquery, threePointArc or tangentArc can be used
# We'll use a series of points for the arc to ensure proper shape
N_ARC = 64

# Left arc: center (center1_x, 0), from 180° to 0° (clockwise)
for k in range(1, N_ARC + 1):
    angle = math.radians(180 - 180 * k / N_ARC)  # 180 to 0
    px = center1_x + radius * math.cos(angle)
    pz = radius * math.sin(angle)
    wp = wp.lineTo(px, pz)

# Bottom line: from left arc bottom (angle 0°) to right arc bottom (angle 0°)
# At angle 0°, the point is (center1_x + radius, 0) = (20.0, 0.0)
# But we need to go to the bottom of the right arc at angle 0° which is (center2_x + radius, 0) = (48.0, 0.0)
# Wait, let's reconsider the geometry.
# The left arc goes from 180° (leftmost) to 0° (rightmost of left arc).
# At 0°, the point is (center1_x + radius, 0) = (20.0, 0.0).
# The bottom line should go from (center1_x + radius, 0) to (center2_x - radius, 0)? No.
# Let's re-examine the design plan:
# The stadium has two arcs at the ends and straight lines connecting them.
# The arcs are semicircles. The left arc center is at (center1_x, 0) = (10.0, 0.0).
# The right arc center is at (center2_x, 0) = (38.0, 0.0).
# The straight lines connect the top and bottom of the arcs.
# The left arc goes from top (angle 90°) to bottom (angle -90°) on the left side.
# The right arc goes from bottom (angle -90°) to top (angle 90°) on the right side.
# The top line connects the top of the left arc (angle 90°) to the top of the right arc (angle 90°).
# The bottom line connects the bottom of the left arc (angle -90°) to the bottom of the right arc (angle -90°).

# Let's rebuild correctly:
# Start at the top of the left arc: (center1_x, radius) = (10.0, 10.0)
# Left arc: from 90° to -90° (clockwise) - this is the left semicircle
# Bottom line: from (center1_x, -radius) to (center2_x, -radius)
# Right arc: from -90° to 90° (clockwise) - this is the right semicircle
# Top line: from (center2_x, radius) to (center1_x, radius)

# Clear and rebuild
wp = cq.Workplane("XZ")

# Start at top of left arc
wp = wp.moveTo(center1_x, radius)

# Left arc: from 90° to -90° (clockwise)
for k in range(1, N_ARC + 1):
    angle = math.radians(90 - 180 * k / N_ARC)  # 90 to -90
    px = center1_x + radius * math.cos(angle)
    pz = radius * math.sin(angle)
    wp = wp.lineTo(px, pz)

# Bottom line: from left arc bottom to right arc bottom
wp = wp.lineTo(center2_x, -radius)

# Right arc: from -90° to 90° (clockwise)
for k in range(1, N_ARC + 1):
    angle = math.radians(-90 - 180 * k / N_ARC)  # -90 to 90 going clockwise? No, clockwise means decreasing angle
    # Actually, from -90° to 90° clockwise means going through -180° (or 180°)
    # Let's use: from -90° to 90° going counter-clockwise (increasing angle)
    angle = math.radians(-90 + 180 * k / N_ARC)  # -90 to 90
    px = center2_x + radius * math.cos(angle)
    pz = radius * math.sin(angle)
    wp = wp.lineTo(px, pz)

# Top line: from right arc top to left arc top
wp = wp.lineTo(center1_x, radius)

# Close the wire
wp = wp.close()

# Extrude along Y (positive direction)
result = wp.extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)