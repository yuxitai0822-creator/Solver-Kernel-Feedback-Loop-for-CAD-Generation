import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_03\iter_01/generated.step"

# Design parameters from the design plan:
# Stadium profile: straight_length = 500.0 mm, radius = 50.0 mm
# Extrude distance = 100.0 mm
# The stadium is centered along the x-axis (u direction) from 0 to 500, with arcs at ends.
# The profile lies in the XY plane, extruded in +Z direction.

straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile using cadquery's 2D construction.
# The stadium consists of:
# - Left arc: center at (0, 0), radius 50, from 90° to -90° (or 0 to 180 in the design plan's local UV)
# - Bottom line: from (0, -50) to (500, -50)
# - Right arc: center at (500, 0), radius 50, from -90° to 90° (or 0 to 180)
# - Top line: from (500, 50) to (0, 50)
#
# In cadquery, we can use threePointArc or sagittaArc, but the simplest is to use
# a polyline approximation with arcs discretized, or use the built-in twoPointArc.
# However, to ensure exact geometry and avoid numerical issues, we'll construct the
# stadium using lines and arcs with center points.

# Create a workplane on XY
wp = cq.Workplane("XY")

# Build the stadium wire manually:
# Start at the left arc top point: (0, 50)
# Arc from (0, 50) to (0, -50) with center (0, 0) -> this is a 180° arc
# Line from (0, -50) to (500, -50)
# Arc from (500, -50) to (500, 50) with center (500, 0) -> 180° arc
# Line from (500, 50) back to (0, 50)

# Use the polyline + arc approach with discretization for robustness
N_ARC = 64  # number of segments per arc

# Build the outer wire as a list of points
pts = []

# Left arc: from angle 90° (top) to -90° (bottom), center (0,0), radius 50
for k in range(N_ARC + 1):
    t = math.pi/2 - math.pi * (k / N_ARC)  # from 90° down to -90°
    x = 0 + radius * math.cos(t)
    y = 0 + radius * math.sin(t)
    pts.append((x, y))

# Bottom line: from (0, -50) to (500, -50)
# The last point of the arc is (0, -50), so we add intermediate points for the line
num_line_pts = 2  # just start and end
for k in range(1, num_line_pts + 1):
    frac = k / num_line_pts
    x = 0 + frac * straight_length
    y = -radius
    pts.append((x, y))

# Right arc: from angle -90° (bottom) to 90° (top), center (500,0), radius 50
for k in range(1, N_ARC + 1):
    t = -math.pi/2 + math.pi * (k / N_ARC)  # from -90° up to 90°
    x = straight_length + radius * math.cos(t)
    y = 0 + radius * math.sin(t)
    pts.append((x, y))

# Top line: from (500, 50) back to (0, 50)
for k in range(1, num_line_pts):
    frac = k / num_line_pts
    x = straight_length - frac * straight_length
    y = radius
    pts.append((x, y))

# Now create the wire from points
wire = cq.Workplane("XY").polyline(pts).close().extrude(extrude_distance)

# Alternative: use the built-in twoPointArc for cleaner geometry
# But the above discretization is reliable.

result = wire

exporters.export(result, OUT_STEP_PATH)