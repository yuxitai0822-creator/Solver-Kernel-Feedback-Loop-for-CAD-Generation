import cadquery as cq

# Design Plan: extruded profile with a circular hole
# The profile consists of an outer shape (a rectangle with rounded corners approximated by a circle at the top)
# and an inner circle (hole). The extrusion is 18.0 mm in the +w direction.

# Create the outer profile: a rectangle with a circular arc at the top.
# From the design plan, the outer ring has 4 curves:
#   line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
#   line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
#   line from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
#   circle centered at (2.3181225581176115, 1.7490620724718653) radius 1.4
# Note: The circle at the top connects the two vertical lines.

# Build the outer wire manually using edges.
# We'll create a workplane and then use 2D geometry.

# Start with a workplane
result = cq.Workplane("XY")

# Build the outer profile as a closed wire
# Points for the rectangle base: bottom-left, bottom-right, top-right, top-left (with arc)
# The circle center is at (2.3181225581176115, 1.7490620724718653) radius 1.4
# The circle intersects the vertical lines at y=1.7936743887554851 (approx top of vertical lines)
# Actually the vertical lines go from y=0 to y=1.7936743887554851
# The circle center y is 1.7490620724718653, radius 1.4, so top of circle is at y=3.1490620724718653
# But the design plan shows the outer ring has only 4 curves: two vertical lines, one bottom horizontal, and one circle at top.
# So the shape is like a rectangle with a circular cap at the top.

# Let's reconstruct using a polygon and a circle, then combine.
# Actually easier: create a rectangle and then add a circle at the top, but that would be overlapping.
# Better: create the shape as a single closed wire.

# The bottom horizontal line: from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
# Left vertical: from (0.9188335453558412, 0.0) to (0.9188335453558412, 1.7936743887554851)
# Right vertical: from (3.7174115708793822, 0.0) to (3.7174115708793822, 1.7936743887554851)
# The top is a circle arc from left vertical top to right vertical top, centered at (2.3181225581176115, 1.7490620724718653) radius 1.4

# The circle center is at (2.3181225581176115, 1.7490620724718653)
# The left vertical top is at (0.9188335453558412, 1.7936743887554851)
# The right vertical top is at (3.7174115708793822, 1.7936743887554851)
# Check distances from center:
# Left: dx = 0.9188335453558412 - 2.3181225581176115 = -1.3992890127617703, dy = 1.7936743887554851 - 1.7490620724718653 = 0.0446123162836198
# Distance = sqrt(1.399289^2 + 0.044612^2) ≈ 1.400 (close to 1.4)
# Right: dx = 3.7174115708793822 - 2.3181225581176115 = 1.3992890127617707, dy = same = 0.0446123162836198
# Distance ≈ 1.400, so both points lie on the circle.

# So the top arc is the part of the circle between these two points, going the long way (since the circle is the top cap).
# The circle is centered at (2.3181225581176115, 1.7490620724718653) radius 1.4.
# The arc from left point to right point going clockwise (or counterclockwise) should be the top half.

# We'll build the outer wire using edges.

# Create points
p1 = (0.9188335453558412, 0.0)
p2 = (3.8000000566244125, 0.0)
p3 = (3.7174115708793822, 1.7936743887554851)
p4 = (0.9188335453558412, 1.7936743887554851)
center = (2.3181225581176115, 1.7490620724718653)
radius = 1.4

# Build the outer wire
# We'll use a workplane and then create a closed wire from edges.
# Since cadquery doesn't directly support arbitrary arcs easily, we can use a workplane and then extrude.
# Alternative: create a 2D sketch using cq.Workplane and then polyline + arc.

# Let's use a simpler approach: create the shape as a combination of a rectangle and a circle, then fuse.
# But the design plan shows a single closed outer ring, so we need to create that shape.

# Actually, we can create the outer profile by:
# 1. Create a rectangle from (0.9188, 0) to (3.8, 1.7937)
# 2. Create a circle at (2.3181, 1.7491) radius 1.4
# 3. Intersect? No, the outer shape is the union of the rectangle and the circle, but the circle extends above the rectangle.
# The outer shape is like a rectangle with a circular top. So union of rectangle and circle, then take the outer boundary.

# Let's do that: create a rectangle and a circle, fuse them, then get the outer wire.

# But we also have an inner hole: a circle centered at same center with radius 1.25

# So the final shape is: outer = rectangle + circle (radius 1.4), inner = circle (radius 1.25) subtracted.

# Let's build step by step.

# First, create the outer shape
rect = cq.Workplane("XY").rect(3.8 - 0.9188335453558412, 1.7936743887554851).translate((0.9188335453558412 + 3.8)/2, 1.7936743887554851/2)
# Actually rect center at ( (0.9188+3.8)/2, 1.7937/2 ) = (2.3594, 0.8968)
# But the rectangle bottom-left is at (0.9188, 0), top-right at (3.8, 1.7937)

# Better: use a workplane and build the shape directly.

# Let's use a different approach: create the outer wire using cq.Wire and cq.Edge.
# But that's complex. Instead, use cq.Workplane with polyline and arc.

# We'll create a workplane, then use moveTo, lineTo, and threePointArc or sagittaArc.

# The outer shape: start at bottom-left (0.9188, 0), go right to (3.8, 0), go up to (3.7174, 1.7937), 
# then arc to (0.9188, 1.7937) with center (2.3181, 1.7491), then close back to start.

# The arc from (3.7174, 1.7937) to (0.9188, 1.7937) with center (2.3181, 1.7491) is a circular arc.
# The angle from center to right point: vector (1.3993, 0.0446), angle = atan2(0.0446, 1.3993) ≈ 1.825°
# The angle from center to left point: vector (-1.3993, 0.0446), angle = atan2(0.0446, -1.3993) ≈ 178.175°
# So the arc goes from 1.825° to 178.175° (counterclockwise), which is the top arc (about 176.35°).
# In cadquery, we can use threePointArc: start point, middle point, end point.
# The middle point of the arc is at the top of the circle: center + (0, radius) = (2.3181, 3.1491)

# So the outer wire:
# start at (0.9188, 0)
# line to (3.8, 0)
# line to (3.7174, 1.7937)
# threePointArc to (0.9188, 1.7937) via (2.3181, 3.1491)
# close

# Then create a circle for the inner hole.

# Let's implement this.

# Create the outer profile
outer = (
    cq.Workplane("XY")
    .moveTo(0.9188335453558412, 0.0)
    .lineTo(3.8000000566244125, 0.0)
    .lineTo(3.7174115708793822, 1.7936743887554851)
    .threePointArc((2.3181225581176115, 3.1490620724718653), (0.9188335453558412, 1.7936743887554851))
    .close()
)

# Now create the inner circle (hole)
inner = cq.Workplane("XY").circle(1.2500000000000002).translate((2.3181225581176115, 1.7490620724718653))

# Combine: outer minus inner
result = outer.cut(inner)

# Extrude by 18.0 mm in the +z direction
result = result.extrude(18.0)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104283_e5646f96_0001\\neg_01/generated.step")
