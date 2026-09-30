import cadquery as cq

# Design Plan: Extruded profile with a circular hole
# The profile consists of an outer shape (rectangle with rounded corners approximated by a circle) and an inner circle (hole).
# Based on the curves, the outer profile is defined by:
#   - A vertical line from (0.9188, 1.7937) to (0.9188, 0.0)
#   - A horizontal line from (0.9188, 0.0) to (3.8000, 0.0)
#   - A vertical line from (3.7174, 1.7937) to (3.7174, 0.0)  (note: the top horizontal is missing, but the circle at center (2.3181, 1.7491) radius 1.4 connects the two vertical lines at the top)
#   - A circle at center (2.3181, 1.7491) radius 1.4
# The inner hole is a circle at same center with radius 1.25
# Extrude distance: 18.0 mm

# Build the outer profile using a workplane and sketching the edges.
# We'll create the shape by combining a rectangle with a circle at the top.
# Actually, the outer boundary is: left vertical, bottom horizontal, right vertical, and a circular arc at the top.
# The circle center is at (2.3181, 1.7491), radius 1.4. The left vertical ends at y=1.7937, right vertical ends at y=1.7937.
# The circle passes through these endpoints? Let's check: distance from center to left point (0.9188,1.7937) = sqrt((2.3181-0.9188)^2 + (1.7491-1.7937)^2) = sqrt(1.3993^2 + (-0.0446)^2) ≈ 1.4, yes.
# Similarly for right point (3.7174,1.7937): sqrt((2.3181-3.7174)^2 + (1.7491-1.7937)^2) = sqrt((-1.3993)^2 + (-0.0446)^2) ≈ 1.4.
# So the outer shape is a rectangle with a circular top (like a stadium shape but with a full circle? Actually it's a rectangle with a semicircular top? No, the circle is full, but only the top arc is part of the boundary; the bottom half of the circle is inside the rectangle? Wait, the rectangle bottom is at y=0, top of rectangle would be at y=1.7937, but the circle center is at y=1.7491, radius 1.4, so the circle extends down to y=0.3491, which is inside the rectangle. So the outer boundary is: left vertical from y=0 to y=1.7937, then circular arc from left point to right point (the top arc of the circle), then right vertical down to y=0, then bottom horizontal back to left. That's a closed shape.
# So we can create this as a single wire: start at (0.9188, 0), line to (0.9188, 1.7937), arc to (3.7174, 1.7937) via circle center (2.3181, 1.7491), line to (3.7174, 0), line to (0.9188, 0).

# However, CadQuery's Workplane doesn't directly support arcs defined by center and two endpoints easily. We can use three-point arc or use the circle and trim.
# Alternative: Create the outer shape by making a rectangle and then cutting a circle? No, the outer shape is convex with a circular top.
# Better: Use a polyline for the straight edges and a three-point arc for the top.
# Points: A=(0.9188, 0), B=(0.9188, 1.7937), C=(3.7174, 1.7937), D=(3.7174, 0)
# Arc from B to C passing through a point on the circle. The circle center is (2.3181, 1.7491), radius 1.4. The topmost point of the circle is at (2.3181, 1.7491+1.4=3.1491). But that's above B and C? Actually B and C are at y=1.7937, which is below the center? No, center y=1.7491, so B and C are slightly above center (1.7937 > 1.7491). The topmost point is at y=3.1491, which is much higher. So the arc from B to C going through the top of the circle would be a large arc. But the design plan shows the circle as part of the boundary, meaning the arc from B to C is the part of the circle that goes above B and C? Wait, the circle radius is 1.4, center at (2.3181, 1.7491). The points B and C are at y=1.7937, which is above the center. So the arc from B to C that is part of the outer boundary must be the minor arc that goes above (since the circle extends upward to y=3.1491). So the arc goes from B up to the top and down to C. That is a convex arc.
# So we can define a three-point arc: start B, end C, midpoint at (2.3181, 3.1491) (top of circle).

# Let's build the outer wire.

# But we also have an inner hole: circle at same center with radius 1.25.

# We'll create the base shape on the XY plane, then extrude.

# Note: The coordinates in the design plan are in the UV frame. We'll assume XY plane.

# Build outer profile
outer = (
    cq.Workplane("XY")
    .moveTo(0.9188335453558412, 0.0)
    .lineTo(0.9188335453558412, 1.7936743887554851)  # left vertical
    .threePointArc(
        (2.3181225581176115, 3.149062072471865),  # top of circle (center y + radius)
        (3.7174115708793822, 1.7936743887554851)   # right point
    )
    .lineTo(3.7174115708793822, 0.0)  # right vertical
    .close()  # line back to start
)

# Now create the inner hole as a circle
inner = (
    cq.Workplane("XY")
    .circle(1.2500000000000002)
)

# Combine: create the outer shape, then cut the inner circle
# We need to position the inner circle at the correct center
result = (
    cq.Workplane("XY")
    .polyline([
        (0.9188335453558412, 0.0),
        (0.9188335453558412, 1.7936743887554851),
        (3.7174115708793822, 1.7936743887554851),
        (3.7174115708793822, 0.0)
    ])
    .close()
    .extrude(18.0)
)

# The above creates a rectangular block. We need to add the circular top.
# Better approach: Create the full outer shape as a single closed wire using a polyline and an arc.

# Let's use a different method: create the outer shape by building a 2D profile with edges.
# We'll use the Workplane's wire construction capabilities.

# Create a workplane and add edges one by one.
# Start with a point, then line, arc, line, close.

# Actually, we can use the 'polyline' method for straight segments and 'threePointArc' for the arc.
# But polyline expects a list of points and creates lines between them. We can't mix arc in polyline.
# So we'll build the wire manually using the 'moveTo', 'lineTo', 'threePointArc', 'lineTo', 'close' sequence.

# Let's do it step by step:

# Create a new workplane
wp = cq.Workplane("XY")

# Move to start point
wp = wp.moveTo(0.9188335453558412, 0.0)

# Line to left top
wp = wp.lineTo(0.9188335453558412, 1.7936743887554851)

# Arc to right top (three point arc: start is current point, end is (3.7174, 1.7937), midpoint is top of circle)
wp = wp.threePointArc(
    (2.3181225581176115, 3.149062072471865),  # midpoint (top of circle)
    (3.7174115708793822, 1.7936743887554851)   # end point
)

# Line to right bottom
wp = wp.lineTo(3.7174115708793822, 0.0)

# Close the wire (line back to start)
wp = wp.close()

# Now we have the outer profile as a closed wire. Extrude it.
outer_solid = wp.extrude(18.0)

# Now cut the inner hole: create a circle at the center and extrude through
inner_hole = (
    cq.Workplane("XY")
    .moveTo(2.3181225581176115, 1.7490620724718653)
    .circle(1.2500000000000002)
    .extrude(18.0)
)

# Subtract inner hole from outer solid
result = outer_solid.cut(inner_hole)

# Export
import cadquery as cq
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0001\\neg_02/generated.step")