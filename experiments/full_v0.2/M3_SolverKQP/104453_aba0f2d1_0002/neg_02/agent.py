import cadquery as cq

# Design Plan: extruded stadium (ArmRest v1)
# Dimensions: straight_length=500.0, radius=50.0, extrude_distance=100.0
# Note: The design plan uses a stadium profile with two arcs (radius 5.0) and two lines (length 50.0).
# However, the dimensions section says straight_length=500.0 and radius=50.0.
# The profile curves in the plan show radius=5.0 and line length 50.0 (spanning from 0 to 50 in u).
# This is inconsistent: the curves describe a small stadium (total length 60, width 10),
# but the dimensions say straight_length=500.0 and radius=50.0 (total length 600, width 100).
# We follow the explicit dimensions (straight_length=500, radius=50) as they are marked "explicit_dimension"
# and the curves appear to be scaled incorrectly (possibly a compiler error).
# The validation intents expect span_u=600, span_v=100, span_w=100, which matches the larger dimensions.

# Build the stadium profile
straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Create the stadium profile using CadQuery's built-in stadium shape
# We'll construct it manually: two arcs and two lines
# Center of left arc at (0,0), right arc at (straight_length, 0)
# The arcs go from 90 to -90 (top to bottom) for left arc, and -90 to 90 for right arc
# But the design plan uses 0 to 180 for left arc and 0 to 180 for right arc (different orientation)
# We'll follow the plan's coordinate system: u along x, v along y

# Build the wire using edges
left_arc = cq.Edge.makeCircle(radius, cq.Vector(0, 0), cq.Vector(0, 0, 1), 90.0, -90.0)  # top to bottom
right_arc = cq.Edge.makeCircle(radius, cq.Vector(straight_length, 0), cq.Vector(0, 0, 1), -90.0, 90.0)  # bottom to top
bottom_line = cq.Edge.makeLine(cq.Vector(0, -radius), cq.Vector(straight_length, -radius))
top_line = cq.Edge.makeLine(cq.Vector(straight_length, radius), cq.Vector(0, radius))

# Combine into a wire
wire = cq.Wire.assembleEdges([left_arc, bottom_line, right_arc, top_line])

# Make a face from the wire
face = cq.Face.makeFromWires(wire)

# Extrude along z (w direction)
result = cq.Workplane("XY").placeSketch(cq.Sketch(face)).extrude(extrude_distance)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
