import cadquery as cq

# Design Plan: Extruded profile with a circular hole
# The profile consists of an outer shape (rectangle with rounded corners via circle arcs) and an inner circle (hole).
# The outer shape is defined by four curves: two vertical lines and two arcs (circles) at the top and bottom.
# Actually, the plan shows two profiles: first profile has 4 curves (line, line, line, circle) but that seems incomplete.
# The second profile has an outer ring (circle, line, circle, line) and an inner ring (circle).
# Interpreting: The shape is a rectangle with semicircular ends (like a stadium shape) with a concentric circular hole.
# The rectangle width = 3.8000000566244125 - 0.9188335453558412 = 2.8811665112685713 mm (but scaled?)
# The height = 1.7936743887554851 mm (vertical lines).
# The outer arcs have radius 1.4 mm, center at (2.3181225581176115, 1.7490620724718653).
# The inner hole has radius 1.2500000000000002 mm, same center.
# Extrude distance = 18.0 mm.

# Build the profile on the XY plane, then extrude in Z direction.

# Define points and dimensions
center_x = 2.3181225581176115
center_y = 1.7490620724718653
outer_radius = 1.4
inner_radius = 1.2500000000000002

# The rectangle part: left vertical line at x = 0.9188335453558412, right vertical line at x = 3.7174115708793822
# But note: the right vertical line end_uv x is 3.7174115708793822, start_uv x is 3.7174115708793822 (same).
# The bottom horizontal line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0).
# The top horizontal line? Actually the arcs connect the vertical lines at the top.
# The arcs are circles with center at (center_x, center_y) and radius 1.4.
# The arcs likely connect the top ends of the vertical lines.
# Let's reconstruct the outer profile as a closed wire.

# We'll create the outer shape by:
# - Start at left bottom corner: (0.9188335453558412, 0.0)
# - Line to right bottom corner: (3.8000000566244125, 0.0)  (but note the right vertical line starts at 3.7174115708793822, so there's a discrepancy)
# Actually the plan shows: line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0).
# Then the right vertical line from (3.7174115708793822, 0.0) to (3.7174115708793822, 1.7936743887554851).
# Then the top arc (circle) from (3.7174115708793822, 1.7936743887554851) to (0.9188335453558412, 1.7936743887554851) with center (center_x, center_y) radius 1.4.
# Then the left vertical line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0).

# But the bottom line goes to 3.8000, while the right vertical is at 3.7174. This might be a slight inconsistency.
# We'll use the vertical line x-coordinate as the right boundary: 3.7174115708793822.
# The bottom line will go from left x to right x.

left_x = 0.9188335453558412
right_x = 3.7174115708793822
top_y = 1.7936743887554851
bottom_y = 0.0

# Create the outer profile as a wire
# We'll use a workplane and build the shape.

# Start with a workplane
result = cq.Workplane("XY").workplane(offset=0.0)

# Build the outer shape: a rectangle with semicircular ends.
# Actually it's a slot shape: two vertical lines and two arcs.
# We can use the slot2D method or build manually.
# Let's build manually using polyline and arc.

# Define points for the outer profile
p1 = (left_x, bottom_y)
p2 = (right_x, bottom_y)
p3 = (right_x, top_y)
p4 = (left_x, top_y)

# Create the outer wire
outer_wire = (
    cq.Workplane("XY")
    .moveTo(p1[0], p1[1])
    .lineTo(p2[0], p2[1])
    .lineTo(p3[0], p3[1])
    .threePointArc((center_x, top_y + outer_radius), (p4[0], p4[1]))  # arc from p3 to p4
    .lineTo(p1[0], p1[1])
    .close()
    .wire()
)

# Actually the arc should be a circle arc from p3 to p4 with center at (center_x, center_y).
# The threePointArc needs three points: start, middle, end.
# Start = p3, end = p4, middle = (center_x, center_y + outer_radius) or (center_x, center_y - outer_radius)?
# Since the arc is at the top, the middle point should be above the center.
# The arc goes from right top to left top, passing through the top of the circle.
# So middle = (center_x, center_y + outer_radius)

# Let's redo properly:
# We'll create the outer shape as a closed wire using edges.

# Build the base shape: a rectangle with rounded ends (slot).
# The slot has length = right_x - left_x, width = 2*outer_radius? Actually the height is top_y - bottom_y = 1.7937.
# But the arc radius is 1.4, so the total height should be 2*1.4 = 2.8 if it's a full semicircle.
# However top_y = 1.7937, which is less than 2*1.4 = 2.8. So the arcs are not full semicircles; they are circular arcs.
# The center is at y=1.749, radius=1.4, so the top of the circle is at y=3.149, bottom at y=0.349.
# The vertical lines go from y=0 to y=1.7937. So the arcs connect the tops of the vertical lines.
# The arc from p3 to p4: p3=(right_x, top_y), p4=(left_x, top_y). The center is at (center_x, center_y).
# The arc angle: from the center, the vector to p3 is (right_x - center_x, top_y - center_y) = (1.399289, 0.044612)
# The vector to p4 is (left_x - center_x, top_y - center_y) = (-1.399289, 0.044612)
# So the arc is symmetric and goes through the top of the circle? The top of the circle is at (center_x, center_y + radius) = (2.3181, 3.1491).
# But top_y = 1.7937, so the arc does not reach the top of the circle. It's a smaller arc.
# We can create this arc using three points: p3, a point on the arc, and p4.
# The midpoint of the arc (in terms of angle) would be at (center_x, center_y + radius * cos(theta))? Actually the arc is symmetric.
# The middle point of the arc (in terms of x) is at x=center_x, y = center_y + sqrt(radius^2 - (center_x - left_x)^2)?
# But we can just use threePointArc with a point that lies on the circle.
# The circle equation: (x - center_x)^2 + (y - center_y)^2 = radius^2.
# At x = center_x, y = center_y + radius = 3.1491. But that's above top_y.
# Actually the arc from p3 to p4 is the upper part of the circle. The points p3 and p4 are on the circle.
# Check: (right_x - center_x)^2 + (top_y - center_y)^2 = (1.399289)^2 + (0.044612)^2 = 1.9580 + 0.00199 = 1.9600 = 1.4^2. Yes.
# So p3 and p4 are on the circle. The arc between them is the upper arc (going through the top of the circle).
# The top of the circle is at (center_x, center_y + radius) = (2.3181, 3.1491).
# So the threePointArc from p3 to p4 with middle point at (center_x, center_y + radius) will create the correct arc.

# Let's build the outer profile correctly.

# Create the outer wire using edges
outer = (
    cq.Workplane("XY")
    .moveTo(left_x, bottom_y)
    .lineTo(right_x, bottom_y)
    .lineTo(right_x, top_y)
    .threePointArc((center_x, center_y + outer_radius), (left_x, top_y))
    .lineTo(left_x, bottom_y)
    .close()
)

# Now create the inner circle (hole)
inner = (
    cq.Workplane("XY")
    .circle(inner_radius)
    .moveTo(center_x, center_y)
)

# Combine: outer profile with inner hole
# We can use the workplane to create a face with a hole.
# First create the outer face, then cut the inner circle.

# Build the base shape
base = (
    cq.Workplane("XY")
    .moveTo(left_x, bottom_y)
    .lineTo(right_x, bottom_y)
    .lineTo(right_x, top_y)
    .threePointArc((center_x, center_y + outer_radius), (left_x, top_y))
    .lineTo(left_x, bottom_y)
    .close()
    .extrude(18.0)
)

# Now cut the inner hole
# We need to create a circle at the center and cut through
result = (
    base
    .faces(">Z")  # top face
    .workplane()
    .circle(inner_radius)
    .cutThruAll()
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\104283_e5646f96_0001\neg_02/generated.step")
