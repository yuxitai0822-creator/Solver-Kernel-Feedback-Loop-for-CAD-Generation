import cadquery as cq
from cadquery import exporters
import math

# Design Plan: ArmRest v1 - stadium extrusion
# Stadium profile: straight length 500mm, radius 50mm, extrude 100mm
# The previous script had incorrect dimensions (straight length 500 vs 50, radius 50 vs 5, extrude 150 vs 100)
# and used a complex history-based approach. This script directly implements the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_01\iter_00\generated.step"

# Stadium dimensions from design plan
straight_length = 500.0  # mm (inferred from point span)
radius = 50.0  # mm (from curve_field)
extrude_distance = 100.0  # mm (explicit dimension)

# Build stadium profile in XY plane
# Stadium: two semicircles (radius) connected by two straight lines
# Center of left arc at (0,0), right arc at (straight_length, 0)
# The profile spans from x=0 to x=straight_length, y from -radius to +radius

wp = cq.Workplane("XY")

# Build the stadium profile using a polyline with arcs
# Start at left end of bottom line: (0, -radius)
# Go right along bottom line to (straight_length, -radius)
# Arc up to (straight_length, radius)
# Go left along top line to (0, radius)
# Arc down to (0, -radius)

# Use the workplane to create the profile
# First, create the points for the stadium shape
pts = [
    (0, -radius),  # start bottom-left
    (straight_length, -radius),  # bottom-right
    (straight_length, radius),  # top-right
    (0, radius),  # top-left
]

# Build the wire using lines and arcs
# We'll use a different approach: create the full stadium as a closed wire
# using the workplane's polyline and threePointArc methods

# Start at bottom-left
s = cq.Workplane("XY").moveTo(0, -radius)

# Bottom line to right
s = s.lineTo(straight_length, -radius)

# Right arc (semicircle going up)
s = s.threePointArc((straight_length + radius, 0), (straight_length, radius))

# Top line to left
s = s.lineTo(0, radius)

# Left arc (semicircle going down)
s = s.threePointArc((-radius, 0), (0, -radius))

# Close the wire
s = s.close()

# Extrude the profile
result = s.extrude(extrude_distance)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
