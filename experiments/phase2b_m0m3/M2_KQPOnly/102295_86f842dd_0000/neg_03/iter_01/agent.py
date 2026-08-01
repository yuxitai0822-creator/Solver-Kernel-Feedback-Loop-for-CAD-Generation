import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_03\iter_01/generated.step"

# Design Plan: extruded stadium
# Profile: stadium shape with straight_length=28.0 mm, radius=10.0 mm
# Extrude: 4.0 mm in +w direction (which is +Y in world)
# The stadium is defined in the XZ plane (u=x, v=z, w=y)
# Dimensions: straight_length=28.0, radius=10.0
# Total width = 2*radius + straight_length = 20 + 28 = 48.0
# Height = 2*radius = 20.0
# Center at origin: left arc center at (-14, 0), right arc center at (14, 0)

radius = 10.0
straight_length = 28.0
half_straight = straight_length / 2.0

# Build stadium profile in XZ plane using proper cadquery arc and line operations
wp = cq.Workplane("XZ")

# Start at left end of top line: (-half_straight, radius)
# Go clockwise: top line from left to right, right arc (top to bottom), bottom line right to left, left arc (bottom to top)
# Use threePointArc for proper arcs

# Build the stadium as a closed wire using cadquery's built-in arc and line methods
# Start at the left end of the top line
s = wp.moveTo(-half_straight, radius)

# Top line from left to right
s = s.lineTo(half_straight, radius)

# Right arc: from (half_straight, radius) to (half_straight, -radius) with center at (half_straight, 0)
# Use threePointArc: start point is current position, end point is (half_straight, -radius), mid point is (half_straight + radius, 0)
s = s.threePointArc((half_straight + radius, 0), (half_straight, -radius))

# Bottom line from right to left
s = s.lineTo(-half_straight, -radius)

# Left arc: from (-half_straight, -radius) to (-half_straight, radius) with center at (-half_straight, 0)
# Use threePointArc: start point is current position, end point is (-half_straight, radius), mid point is (-half_straight - radius, 0)
s = s.threePointArc((-half_straight - radius, 0), (-half_straight, radius))

# Close the wire
s = s.close()

# Extrude in +Y direction (w direction) by 4.0 mm
result = s.extrude(4.0)

# Export
exporters.export(result, OUT_STEP_PATH)