import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm
#
# The stadium profile consists of two arcs (radius 10) and two straight lines (length 28).
# The arcs are centered at (10, 0) and (38, 0) in the local UV plane.
# The straight lines connect the arc endpoints.
#
# The extrusion direction is +w (which maps to +Y in the global frame).
# The profile lies in the XZ plane (U -> X, V -> Z).

radius = 10.0
straight_length = 28.0
extrude_distance = 4.0

# Build the stadium profile using CadQuery's 2D primitives.
# We'll create a wire from arcs and lines.

# Define points for the stadium in the XZ plane (U=X, V=Z)
# Arc centers: (radius, 0) and (radius + straight_length, 0)
center1_x = radius
center2_x = radius + straight_length

# Arc endpoints (top and bottom)
# Arc 1 (left): from (center1_x, -radius) to (center1_x, radius) going counterclockwise (0 to 180 deg)
# Arc 2 (right): from (center2_x, radius) to (center2_x, -radius) going counterclockwise (0 to 180 deg)
# Lines: bottom line from (center1_x, -radius) to (center2_x, -radius)
#        top line from (center2_x, radius) to (center1_x, radius)

# Build the profile as a closed wire
# Start at bottom-left arc endpoint
p0 = (center1_x, -radius)
p1 = (center1_x, radius)   # top-left
p2 = (center2_x, radius)   # top-right
p3 = (center2_x, -radius)  # bottom-right

# Create the stadium shape using a simple approach: make a 2D sketch and extrude
# We'll use cq.Workplane to build the profile

result = (
    cq.Workplane("XZ")
    .moveTo(center1_x, -radius)
    .threePointArc((center1_x + radius, 0), (center1_x, radius))  # left arc (0 to 180 deg)
    .lineTo(center2_x, radius)  # top line
    .threePointArc((center2_x - radius, 0), (center2_x, -radius))  # right arc (0 to 180 deg)
    .lineTo(center1_x, -radius)  # bottom line
    .close()
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102295_86f842dd_0000\neg_02/generated.step")
