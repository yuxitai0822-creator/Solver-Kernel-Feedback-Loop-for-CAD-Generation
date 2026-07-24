import cadquery as cq

# Design Plan: Extruded profile with a circular hole
# The profile consists of an outer shape (rectangle with rounded corners via circle arcs) and an inner circle (hole).
# The outer shape is defined by four curves: two vertical lines and two arcs (circles) at the ends.
# The inner hole is a circle concentric with the outer arcs.

# Dimensions inferred from the design plan (in mm, after cm->mm conversion factor 10):
# Outer shape: width = 3.8000000566244125 - 0.9188335453558412 = 2.8811665112685713 mm? Wait, the values are in cm originally? 
# The design plan says unit_conversion_applied: cm_to_mm (x10). So the numbers in the plan are already in mm? 
# Actually the plan says unit is mm, but the compiler note says cm_to_mm (x10). 
# The values in the plan: start_uv x coordinates: 0.9188, 3.8000, etc. These are likely in mm after conversion.
# Let's use them directly as mm.

# Outer profile: two vertical lines at x=0.9188 and x=3.7174, from y=0 to y=1.7937.
# The top ends are connected by a circle arc of radius 1.4 mm centered at (2.3181, 1.7491).
# The bottom ends are connected by a line? Actually the curves list shows:
# curve0: line from (0.9188, 1.7937) to (0.9188, 0.0)
# curve1: line from (0.9188, 0.0) to (3.8000, 0.0)  -- this is the bottom line
# curve2: line from (3.7174, 1.7937) to (3.7174, 0.0) -- but this is reversed? Actually start_uv (3.7174, 1.7937) end_uv (3.7174, 0.0) so it's a vertical line down.
# curve3: circle from (2.3181, 1.7491) radius 1.4 -- this is the top arc.
# But the order seems inconsistent. Let's reconstruct a proper closed loop.

# Better approach: Use the dimensions from the plan.
# The outer shape is like a rectangle with semicircular ends (a stadium shape).
# Width between vertical lines: 3.7174 - 0.9188 = 2.7986 mm
# Height of straight section: 1.7937 mm
# Radius of end arcs: 1.4 mm
# Total length: 1.7937 + 1.4 + 1.4 = 4.5937 mm? Actually the arcs are at the top, so the shape is like a D? 
# Let's look at the curves more carefully.

# The first profile (outer ring) has 4 curves:
# 1. line from (0.9188, 1.7937) to (0.9188, 0.0)  -- left vertical line
# 2. line from (0.9188, 0.0) to (3.8000, 0.0)      -- bottom horizontal line
# 3. line from (3.7174, 1.7937) to (3.7174, 0.0)  -- right vertical line (but reversed direction? Actually start is top, end is bottom)
# 4. circle centered at (2.3181, 1.7491) radius 1.4 -- top arc

# This is a closed loop: left line down, bottom line right, right line up, top arc left.
# But the bottom line goes to x=3.8000, while the right line starts at x=3.7174. There's a slight mismatch.
# Probably the bottom line should end at x=3.7174. Let's use 3.7174 for consistency.

# The inner hole is a circle centered at (2.3181, 1.7491) with radius 1.25 mm.

# Extrude distance: 18.0 mm

# Build the profile using CadQuery's Workplane.

# Define points for the outer profile (in mm):
left_x = 0.9188335453558412
right_x = 3.7174115708793822
bottom_y = 0.0
top_y = 1.7936743887554851
center_x = 2.3181225581176115
center_y = 1.7490620724718653
outer_radius = 1.4
inner_radius = 1.2500000000000002

# Create the outer shape: a rectangle with a circular arc at the top.
# We'll build it as a wire from points and arcs.

# Start at bottom-left corner
p0 = (left_x, bottom_y)
# Bottom-right corner
p1 = (right_x, bottom_y)
# Right vertical line up to the point where the arc starts
p2 = (right_x, top_y)
# The top arc: from right top to left top, centered at (center_x, center_y)
# The arc goes from angle 0 to 180 degrees (assuming center is at the top)
# Actually the center is at (center_x, center_y) and radius 1.4.
# The right top point should be on the circle: (center_x + radius, center_y) = (3.7181, 1.7491) which is close to (3.7174, 1.7937)? 
# There's a discrepancy. Let's use the given points exactly.

# Given the complexity, let's use a simpler approach: create a rectangle and then fillet? No, the shape is specific.

# Alternative: Use the fact that the outer profile is a closed wire. We can create it using cq.Workplane with polyline and arc.

# Let's define the points in order:
pts = [
    (left_x, bottom_y),   # bottom-left
    (right_x, bottom_y),  # bottom-right
    (right_x, top_y),     # top-right (start of arc)
]

# The arc from top-right to top-left, centered at (center_x, center_y)
# We need to find the start and end angles.
start_angle = 0  # point at (center_x + radius, center_y) = (3.7181, 1.7491)
end_angle = 180   # point at (center_x - radius, center_y) = (0.9181, 1.7491)

# But the given top_y is 1.7937, not 1.7491. So the arc center is slightly below the top points.
# The vertical distance from center to top is 1.7937 - 1.7491 = 0.0446 mm.
# The radius is 1.4, so the angle from center to top-right point is arcsin(0.0446/1.4) ≈ 1.83 degrees.
# This is getting too detailed. Let's just use the given points directly.

# Actually, the simplest way: create the outer shape as a rectangle with a circular top.
# But the design plan says the outer ring has 4 curves: 3 lines and 1 circle.
# The circle is the top arc. The lines are left, bottom, right.

# Let's build it step by step using CadQuery's 2D drawing capabilities.

# Create a workplane and draw the outer profile
result = (cq.Workplane("XY")
          .moveTo(left_x, bottom_y)
          .lineTo(right_x, bottom_y)  # bottom edge
          .lineTo(right_x, top_y)     # right edge up
          .threePointArc((center_x, top_y + outer_radius), (left_x, top_y))  # top arc
          .close()  # close back to start
          .extrude(18.0)
)

# Now cut the inner hole
result = (result
          .faces("<Z")  # select the bottom face
          .workplane()
          .circle(inner_radius)
          .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
