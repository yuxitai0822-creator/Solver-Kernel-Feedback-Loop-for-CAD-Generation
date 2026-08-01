import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_03\iter_00\generated.step"

# Design parameters from the design plan
# Stadium profile: straight_length=500.0, radius=50.0 (note: plan says 50.0, not 5.0)
# The plan's curves section has radius=5.0 but dimensions say radius=50.0
# The dimensions section is authoritative: straight_length=500.0, radius=50.0
straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile
# A stadium consists of two semicircles connected by two straight lines
# The total length along u is straight_length + 2*radius = 500 + 100 = 600
# The total width along v is 2*radius = 100

# Create workplane
wp = cq.Workplane("XY")

# Build the stadium profile using lines and arcs
# Start at the bottom-left corner of the left semicircle
# The stadium is centered at origin for simplicity
# Left semicircle center at (0, 0), right semicircle center at (straight_length, 0)

# Build the profile as a closed wire
# Start at the bottom of the left semicircle: (0, -radius)
# Arc from bottom to top of left semicircle (counterclockwise)
# Line from top of left semicircle to top of right semicircle
# Arc from top to bottom of right semicircle (counterclockwise)
# Line from bottom of right semicircle back to bottom of left semicircle

# Use the polyline+arc approach with discretization for robustness
N_ARC = 64

# Build the profile point by point
pts = []

# Left semicircle: from angle -90 to 90 degrees (bottom to top)
for k in range(N_ARC + 1):
    t = -math.pi/2 + math.pi * (k / N_ARC)
    x = radius * math.cos(t)
    y = radius * math.sin(t)
    pts.append((x, y))

# Top line: from left semicircle top to right semicircle top
pts.append((straight_length, radius))

# Right semicircle: from angle 90 to 270 degrees (top to bottom)
for k in range(1, N_ARC + 1):
    t = math.pi/2 + math.pi * (k / N_ARC)
    x = straight_length + radius * math.cos(t)
    y = radius * math.sin(t)
    pts.append((x, y))

# Bottom line: from right semicircle bottom back to left semicircle bottom
pts.append((0, -radius))

# Create the wire from points
result = (
    cq.Workplane("XY")
    .polyline(pts)
    .close()
    .extrude(extrude_distance)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
