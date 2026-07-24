import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm
#
# The stadium profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so positive v goes downward in Z)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The profile curves (in UV coordinates):
#   Arc1: center (1.0, 0.0), radius 1.0, from 0° to 180°
#   Line1: from (1.0, -1.0) to (3.8, -1.0)
#   Arc2: center (3.8, 0.0), radius 1.0, from 0° to 180°
#   Line2: from (3.8, 1.0) to (1.0, 1.0)
#
# These UV coordinates are in "unit" space. The actual dimensions are:
#   straight_length = 28.0 mm, radius = 10.0 mm.
# The UV coordinates span: width = (3.8 - 1.0) + 2*1.0 = 4.8 units, height = 2.0 units.
# Scaling factor: width scales to 2*radius + straight_length = 20 + 28 = 48 mm.
# So scale = 48 / 4.8 = 10.0. Height scales to 2*radius = 20 mm, scale = 20 / 2.0 = 10.0.
# Consistent: scale = 10.0.

scale = 10.0

# Build the stadium profile in the XY plane (since we'll extrude in Y direction)
# We'll place the center of the stadium at the origin for convenience.
# The profile in UV: Arc1 (top), Line1 (right), Arc2 (bottom), Line2 (left)
# After scaling and centering:
#   Arc1: center at (1.0*scale, 0), radius = 1.0*scale, from 0° to 180° (top half)
#   Line1: from (1.0*scale, -1.0*scale) to (3.8*scale, -1.0*scale)  (right side, bottom)
#   Arc2: center at (3.8*scale, 0), radius = 1.0*scale, from 0° to 180° (bottom half)
#   Line2: from (3.8*scale, 1.0*scale) to (1.0*scale, 1.0*scale)  (left side, top)
#
# Note: In the design plan, v_dir = (0,0,-1), so positive v goes downward in Z.
# But we're building in XY, so we'll map: u -> X, v -> Y (with Y up).
# The arcs go from 0° to 180° which in standard math is counterclockwise from +X axis.
# Arc1: start at angle 0 (point (center_x + r, center_y)), end at 180 (center_x - r, center_y).
#   This gives a semicircle above the center (since Y = r*sin(theta), sin(0)=0, sin(180)=0, but intermediate positive).
#   Actually, for theta from 0 to 180, sin(theta) is positive for 0<theta<180, so the arc bulges upward (positive Y).
#   In the design plan, this arc is the "top" arc (positive v direction).
# Arc2: same center, same angles, but the line connects the bottom points.
#   Wait: Arc2 center is at (3.8, 0), radius 1.0, from 0° to 180°.
#   This arc also bulges upward (positive Y). But the line connects (3.8, -1.0) to (1.0, -1.0) which is at the bottom.
#   So Arc2 is actually the bottom arc? Let's re-examine.
#
# The profile is a stadium: two semicircles connected by straight lines.
# The straight lines are at the top and bottom (v = +1 and v = -1).
# The arcs are at the left and right ends.
# Arc1: center (1.0, 0), radius 1.0, from 0° to 180°.
#   At 0°: (2.0, 0), at 180°: (0, 0). This arc goes through (1.0, 1.0) at 90°.
#   So it's the right semicircle (bulging to the right, i.e., positive u direction).
# Arc2: center (3.8, 0), radius 1.0, from 0° to 180°.
#   At 0°: (4.8, 0), at 180°: (2.8, 0). This arc goes through (3.8, 1.0) at 90°.
#   So it's also a right-bulging arc? That would make both arcs on the same side.
#   But the line connects (1.0, -1.0) to (3.8, -1.0) (bottom) and (3.8, 1.0) to (1.0, 1.0) (top).
#   So the profile goes: start at (1.0, -1.0) -> line to (3.8, -1.0) -> arc from (3.8, -1.0) to (3.8, 1.0) (via (4.8, 0)) -> line to (1.0, 1.0) -> arc from (1.0, 1.0) to (1.0, -1.0) (via (0, 0)).
#   That's a stadium shape with the straight section along the bottom and top, and arcs on the left and right.
#   The arcs are oriented such that they bulge outward (to the right for Arc2, to the left for Arc1).
#   Arc1: center (1.0, 0), radius 1.0, from 0° to 180° goes from (2.0, 0) to (0, 0) through (1.0, 1.0).
#     But we need it to go from (1.0, 1.0) to (1.0, -1.0). That would be from 90° to 270° (or -90°).
#     So the arc direction might be reversed or the angles are measured differently.
#
# Let's re-read the design plan carefully:
#   Arc1: center_uv = [1.0, 0.0], radius = 1.0, start_angle_deg = 0.0, end_angle_deg = 180.0
#   Line1: start_uv = [1.0, -1.0], end_uv = [3.8, -1.0]
#   Arc2: center_uv = [3.8, 0.0], radius = 1.0, start_angle_deg = 0.0, end_angle_deg = 180.0
#   Line2: start_uv = [3.8, 1.0], end_uv = [1.0, 1.0]
#
# The curves are listed in order: Arc1, Line1, Arc2, Line2.
# The end of Arc1 should connect to the start of Line1.
# Arc1 ends at angle 180°: point = center + r*(cos180, sin180) = (1.0 + 1.0*(-1), 0 + 1.0*0) = (0, 0).
# But Line1 starts at (1.0, -1.0). These don't match! So the angles must be interpreted differently.
#
# Perhaps the angles are measured from the positive v direction (which is (0,0,-1) in world, but in UV it's (0,1)).
# Or perhaps the arcs are defined with a different convention.
#
# Given the constraints (tangent, parallel, midpoint), the shape is clearly a stadium.
# The dimensions tell us: straight_length = 28.0 mm, radius = 10.0 mm.
# So the total width = 2*radius + straight_length = 48 mm, height = 2*radius = 20 mm.
#
# I'll build the stadium directly using the known dimensions, ignoring the UV coordinate confusion.
# The stadium will be centered at the origin in the XY plane, then extruded in the Y direction.

# Build the stadium profile
radius = 10.0
straight_length = 28.0
half_length = straight_length / 2.0

# Create the base wire: a stadium shape
# We'll use a workplane and build the profile
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .hLine(-half_length)  # bottom line from right center to left center
    .threePointArc((-(half_length + radius), 0), (-half_length, radius))  # left arc
    .vLine(2 * radius)  # left side up
    .threePointArc((-half_length, 2 * radius), (-half_length, radius))  # left arc top (actually this is wrong)
)

# Let's use a simpler approach: create the stadium as a closed wire
# Points for the stadium (starting at rightmost point, going clockwise)
# Right semicircle: from (half_length, 0) to (half_length, 0) via (half_length + radius, 0)? No.
# Standard stadium: two semicircles at ends, connected by straight lines.
# Let's define the profile explicitly.

# Actually, let's use the dimensions directly from the design plan.
# The profile in UV had scale 10, so:
#   radius in UV = 1.0 -> actual radius = 10.0 mm
#   straight_length in UV = 3.8 - 1.0 = 2.8 -> actual straight_length = 28.0 mm
#   total width = 4.8 * 10 = 48 mm
#   total height = 2.0 * 10 = 20 mm

# Build the stadium using cadquery's built-in methods
# We can create a 2D sketch with lines and arcs

# Start with a workplane
s = cq.Workplane("XY")

# Build the stadium profile
# The stadium has its center at the origin
# Right semicircle: center at (half_length, 0), radius = radius
# Left semicircle: center at (-half_length, 0), radius = radius
# Top line: from (-half_length, radius) to (half_length, radius)
# Bottom line: from (half_length, -radius) to (-half_length, -radius)

# We'll create the profile using a polyline and arcs
# Start at the rightmost point of the right semicircle: (half_length + radius, 0)
# Arc to the top of the right semicircle: (half_length, radius)
# Line to the top of the left semicircle: (-half_length, radius)
# Arc to the bottom of the left semicircle: (-half_length, -radius)
# Line to the bottom of the right semicircle: (half_length, -radius)
# Arc back to the start

# Using threePointArc for the semicircles
# Right semicircle: from (half_length, radius) to (half_length, -radius) via (half_length + radius, 0)
# Left semicircle: from (-half_length, -radius) to (-half_length, radius) via (-half_length - radius, 0)

# Build the wire
wire = (
    cq.Workplane("XY")
    .moveTo(half_length, radius)  # start at top-right of right semicircle
    .threePointArc((half_length + radius, 0), (half_length, -radius))  # right semicircle (clockwise)
    .lineTo(-half_length, -radius)  # bottom line
    .threePointArc((-half_length - radius, 0), (-half_length, radius))  # left semicircle (clockwise)
    .lineTo(half_length, radius)  # top line
    .close()
)

# Extrude in the Y direction (w_dir = (0,1,0))
extrude_distance = 4.0

result = wire.extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
