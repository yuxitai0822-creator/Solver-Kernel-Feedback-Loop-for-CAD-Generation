import cadquery as cq

# Design Plan: extruded stadium (ArmRest v1)
# Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
# Note: The design plan uses a stadium profile with two arcs (radius 5.0) and two lines (length 50.0).
# However, the dimensions section says straight_length=500.0 and radius=50.0.
# The profile curves in the plan show radius=5.0 and line length 50.0 (spanning from 0 to 50 in u).
# This discrepancy suggests the plan's profile curves are a scaled-down representation.
# We follow the explicit dimensions: straight_length=500.0, radius=50.0, extrude=100.0.

# Build stadium profile in the XY plane (u=x, v=y), then extrude along Z (w).
# Center the shape at origin for convenience.

# Parameters
straight_length = 500.0  # length of the straight section (distance between arc centers)
radius = 50.0           # radius of the end arcs
extrude_distance = 100.0

# Create the stadium profile using CadQuery's 2D primitives
# We'll build a wire from arcs and lines, then make a face.

# Points for the profile (starting at bottom-left, going clockwise)
# Bottom-left arc center at (0,0), top-left arc center at (0,0) but arcs are on ends.
# Actually: left arc center at (0,0), right arc center at (straight_length, 0)
# Bottom line from (-radius, 0) to (straight_length+radius, 0) but arcs are at ends.
# Standard stadium: two semicircles at ends, connected by lines.

# Let's define the profile in the XY plane.
# Left semicircle (bottom to top): center (0,0), radius, from angle -90 to 90 (or 270 to 90)
# Right semicircle (top to bottom): center (straight_length,0), radius, from angle 90 to 270
# Top line: from (straight_length, radius) to (0, radius)
# Bottom line: from (0, -radius) to (straight_length, -radius)

# Build using CadQuery's 2D workplane
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(0, -radius)  # start at bottom of left arc
    .threePointArc((radius, 0), (0, radius))  # left semicircle (bottom to top)
    .lineTo(straight_length, radius)  # top line
    .threePointArc((straight_length + radius, 0), (straight_length, -radius))  # right semicircle
    .lineTo(0, -radius)  # bottom line
    .close()
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0002\\neg_01/generated.step")
