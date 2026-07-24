import cadquery as cq

# Design Plan: extruded profile with a circular hole
# The profile consists of an outer shape (rectangle with rounded corners via circle arcs) and an inner circle (hole).
# The outer shape is defined by four curves: two vertical lines and two arcs (circles) at the top and bottom.
# However, the design plan describes the outer ring as a composite of lines and a circle arc.
# The inner ring is a circle (hole).
# The extrusion distance is 18.0 mm.

# Based on the UV coordinates:
# Outer ring:
#   Line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
#   Line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
#   Line from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
#   Circle centered at (2.3181225581176115, 1.7490620724718653) radius 1.4
# The circle arc connects the two vertical lines at the top.
# The bottom is a straight line from x=0.9188 to x=3.8000 at y=0.
# But note: the third curve is a line from (3.7174, 1.7937) to (3.7174, 0.0) — this is the right vertical line.
# The fourth curve is a circle (arc) that closes the loop.
# Actually, the outer ring has 4 curves: line, line, line, circle. The circle is the top arc.
# The bottom is a straight line, left and right vertical lines, and a circular arc at the top.
# However, the coordinates suggest the top arc is centered at (2.3181, 1.7491) radius 1.4.
# The left vertical line goes from y=1.7937 to y=0 at x=0.9188.
# The right vertical line goes from y=1.7937 to y=0 at x=3.7174.
# The bottom line goes from (0.9188,0) to (3.8000,0). Note the x mismatch: right vertical ends at 3.7174, bottom ends at 3.8000.
# This might be a slight inconsistency, but we'll approximate.
# The inner ring is a circle centered at (2.3181, 1.7491) radius 1.25.

# We'll build the outer profile as a wire using lines and a three-point arc (since cadquery doesn't have direct circle arc by center/radius on a plane).
# Alternatively, we can use a rectangle with fillet, but the dimensions are specific.
# Let's construct the outer shape precisely:
# Points:
#   P1 = (0.9188335453558412, 1.7936743887554851)  # top-left
#   P2 = (0.9188335453558412, 0.0)                  # bottom-left
#   P3 = (3.8000000566244125, 0.0)                  # bottom-right (note: x=3.8000)
#   P4 = (3.7174115708793822, 1.7936743887554851)  # top-right
# The top edge is a circular arc from P1 to P4 with center at (2.3181225581176115, 1.7490620724718653) radius 1.4.
# The arc should be the shorter path (convex upward).

# We'll create the outer wire using a list of edges.

# First, define points
p1 = (0.9188335453558412, 1.7936743887554851)
p2 = (0.9188335453558412, 0.0)
p3 = (3.8000000566244125, 0.0)
p4 = (3.7174115708793822, 1.7936743887554851)
center = (2.3181225581176115, 1.7490620724718653)
radius_outer = 1.4
radius_inner = 1.2500000000000002

# Build outer wire
# We'll use a workplane and then create a polygon with a circular arc.
# Since cadquery's 2D construction is limited, we can use a spline or approximate with a series of points.
# Better: use a cq.Workplane and then offset or use the 'polyline' and 'threePointArc'.

# Let's create the outer profile as a closed wire:
# Start at p1, line to p2, line to p3, then arc from p3 to p4? No, the arc is at the top from p1 to p4.
# Actually the order: p1 -> p2 (left line), p2 -> p3 (bottom line), p3 -> p4 (right line), p4 -> p1 (top arc).
# But the arc is defined from p1 to p4 with center above? Let's check: center y=1.749, p1 y=1.7937, p4 y=1.7937. The center is slightly below the endpoints, so the arc is convex downward? Actually radius 1.4, distance from center to p1: sqrt((0.9188-2.3181)^2 + (1.7937-1.7491)^2) = sqrt(1.3993^2 + 0.0446^2) ≈ 1.4, so it's a circular arc. The center is below the endpoints, so the arc bulges downward (toward the interior of the shape). That would make the top edge curved inward? That seems odd for a typical shape. But we'll follow the data.

# Let's compute the angle: vector from center to p1: (-1.3993, 0.0446), to p4: (1.3993, 0.0446). The arc from p1 to p4 going the short way (counterclockwise) would go through the bottom (since center is below). So the arc is concave downward (bulging into the shape). That might be correct for a slot-like shape.

# We'll construct using a workplane and then use the 'polyline' and 'threePointArc'.

# Create a workplane on XY plane
s = cq.Workplane("XY")

# Build outer profile
# Start at p1, line to p2, line to p3, then arc from p3 to p4? No, the arc is from p1 to p4. So we need to go from p3 to p4 via a line, then arc from p4 to p1.
# Order: p1 -> p2 (line), p2 -> p3 (line), p3 -> p4 (line), p4 -> p1 (arc).
# But the arc is defined by start p1, end p4, and center. We can use threePointArc if we know a midpoint on the arc.
# The midpoint of the arc (at the bottom of the circle) would be at center - (0, radius) = (2.3181, 1.7491 - 1.4) = (2.3181, 0.3491).
# So we can use threePointArc from p4 to p1 via (2.3181, 0.3491).

mid_arc = (center[0], center[1] - radius_outer)  # (2.3181, 0.3491)

# Build the outer wire
outer = (s
    .moveTo(p1[0], p1[1])
    .lineTo(p2[0], p2[1])
    .lineTo(p3[0], p3[1])
    .lineTo(p4[0], p4[1])
    .threePointArc(mid_arc, p1)
    .close()
)

# Now we need to cut out the inner circle.
# The inner circle is centered at (2.3181, 1.7491) radius 1.25.
# We can create a circle on the same workplane and subtract.

# However, the outer profile is a closed wire; we need to make a face and then extrude.
# We can use the outer wire to create a face, then create a circle hole.

# Alternative: create the outer shape as a solid by extruding the face, then cut a cylinder.

# Let's create the outer face:
outer_face = cq.Workplane("XY").polyline([p1, p2, p3, p4]).close().extrude(18.0)
# But this doesn't include the arc. So we need to use the wire approach.

# Better: use the wire to make a face.
# We can create a wire from edges and then make a face.

# Let's construct edges explicitly:
from cadquery import Vector, Edge, Wire, Face

# Define points as Vectors
v1 = Vector(p1[0], p1[1], 0)
v2 = Vector(p2[0], p2[1], 0)
v3 = Vector(p3[0], p3[1], 0)
v4 = Vector(p4[0], p4[1], 0)
vc = Vector(center[0], center[1], 0)

# Create edges
edge1 = Edge.makeLine(v1, v2)
edge2 = Edge.makeLine(v2, v3)
edge3 = Edge.makeLine(v3, v4)
# Arc from v4 to v1 with center vc (assuming the arc is the shorter path)
# We need to determine the direction. The arc should go from v4 to v1 passing through the midpoint below.
# Use makeCircle with center and two points.
# Edge.makeCircle(radius, center, normal, angle1, angle2) but we need the arc between two points.
# Alternatively, use Edge.makeThreePointArc(v4, mid_arc_point, v1)
mid_point = Vector(mid_arc[0], mid_arc[1], 0)
edge4 = Edge.makeThreePointArc(v4, mid_point, v1)

# Create wire
outer_wire = Wire.makeWire([edge1, edge2, edge3, edge4])
outer_face = Face.makeFace(outer_wire)

# Extrude
solid = cq.Workplane("XY")._add(outer_face).extrude(18.0)

# Now cut the inner hole
# Create a cylinder at the center with radius 1.25, height 18.0
inner_cylinder = cq.Workplane("XY").circle(radius_inner).extrude(18.0)
# Position it at the center
inner_cylinder = inner_cylinder.translate((center[0], center[1], 0))

# Cut
result = solid.cut(inner_cylinder)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
