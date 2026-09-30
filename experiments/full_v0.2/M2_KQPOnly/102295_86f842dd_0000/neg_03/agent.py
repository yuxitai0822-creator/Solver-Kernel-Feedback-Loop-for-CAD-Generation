import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm
#
# The stadium profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The profile curves (in UV):
#   Arc1: center (1.0, 0.0), radius 1.0, start 0°, end 180°
#   Line1: (1.0, -1.0) to (3.8, -1.0)
#   Arc2: center (3.8, 0.0), radius 1.0, start 0°, end 180°
#   Line2: (3.8, 1.0) to (1.0, 1.0)
#
# Note: The UV coordinates are in the design plan's local frame.
# The radius in UV is 1.0, but the actual radius is 10.0 mm.
# This implies a scaling factor of 10 between UV and mm.
# Similarly, the straight length in UV is 2.8, which scales to 28.0 mm.
#
# We build the stadium in the XY plane (u=X, v=Y) and then rotate to match the frame.
# The frame has v_dir = (0,0,-1), so we will mirror or rotate accordingly.

# Build stadium profile in XY plane (u=X, v=Y)
# Center of first arc at (10, 0) in mm (since radius=10)
# Center of second arc at (38, 0) in mm (since 3.8 * 10 = 38)
# Straight length = 28 mm (from 10 to 38)

radius = 10.0
straight_length = 28.0
center1_x = radius  # 10
center2_x = radius + straight_length  # 38

# Build the profile using CadQuery's 2D primitives
# We'll create a wire from arcs and lines

# Start at top of first arc: (center1_x, radius) = (10, 10)
# Arc1 goes from 0° to 180° (counterclockwise) -> from (10+10, 0) to (10-10, 0)?
# Actually: start_angle=0°, end_angle=180° means from rightmost point to leftmost point
#   start: (center1_x + radius*cos(0), center1_y + radius*sin(0)) = (20, 0)
#   end: (center1_x + radius*cos(180), center1_y + radius*sin(180)) = (0, 0)
# But the line goes from (1.0, -1.0) to (3.8, -1.0) in UV, which is bottom side.
# Let's re-express: In UV, the stadium has arcs on left and right, lines top and bottom.
# Arc1: center (1,0), radius 1, start 0°, end 180° -> goes from (2,0) to (0,0) along top half? 
#   Actually 0° is right, 180° is left, going counterclockwise (standard math).
#   So it traces the upper semicircle from right to left.
# Then Line1: from (1, -1) to (3.8, -1) -> bottom line from left to right.
# Then Arc2: center (3.8, 0), radius 1, start 0°, end 180° -> from (4.8, 0) to (2.8, 0) upper semicircle? 
#   Wait, that would be upper again. Let's check: start 0° = rightmost point (4.8,0), end 180° = leftmost (2.8,0).
#   That traces upper semicircle from right to left.
# Then Line2: from (3.8, 1) to (1, 1) -> top line from right to left.
# This gives a closed loop: upper arc1 (right->left), bottom line (left->right), upper arc2 (right->left), top line (right->left)?
# That doesn't close properly. Let's re-examine.

# Actually, the curves are listed in order around the loop:
# 1. Arc: center (1,0), radius 1, start 0°, end 180° -> from (2,0) to (0,0) going counterclockwise (upper half)
# 2. Line: from (1, -1) to (3.8, -1) -> bottom line from left to right
# 3. Arc: center (3.8, 0), radius 1, start 0°, end 180° -> from (4.8,0) to (2.8,0) going counterclockwise (upper half)
# 4. Line: from (3.8, 1) to (1, 1) -> top line from right to left
#
# This doesn't connect properly. The arcs are both upper halves, but the lines are bottom and top.
# Let's think: The stadium shape has two semicircles (left and right) connected by straight lines.
# Left semicircle: center (1,0), radius 1, goes from bottom to top (or top to bottom).
# Right semicircle: center (3.8,0), radius 1, goes from top to bottom (or bottom to top).
# The lines connect the ends of the semicircles.
#
# Typical stadium: left semicircle from bottom-left to top-left, top line from top-left to top-right,
# right semicircle from top-right to bottom-right, bottom line from bottom-right to bottom-left.
#
# In UV: left semicircle center (1,0), radius 1. Bottom point: (1, -1), top point: (1, 1).
#   Arc from bottom to top: start_angle = -90°, end_angle = 90° (or 270° to 90°).
#   But the plan says start_angle=0°, end_angle=180°. That would go from right to left.
#   That doesn't match a left semicircle.
#
# Let's re-read: The curves are:
#   Arc: center (1,0), radius 1, start 0°, end 180°
#   Line: (1,-1) to (3.8,-1)
#   Arc: center (3.8,0), radius 1, start 0°, end 180°
#   Line: (3.8,1) to (1,1)
#
# If we plot these:
#   Arc1: from (2,0) to (0,0) along upper semicircle (counterclockwise)
#   Line1: from (1,-1) to (3.8,-1) [but wait, (1,-1) is not on arc1 end (0,0)]
#   This is inconsistent. The UV coordinates might be in a different orientation.
#
# Given the dimensions: straight_length=28, radius=10, the stadium spans 48 in u and 20 in v.
# The UV coordinates: u from 0 to 4.8 (scaled by 10 gives 0 to 48), v from -1 to 1 (scaled by 10 gives -10 to 10).
# So the profile in UV is: left arc center at u=1 (10mm), right arc center at u=3.8 (38mm), radius 1 (10mm).
# The lines are at v=-1 and v=1 (bottom and top).
#
# The arcs: start_angle=0°, end_angle=180° means they go from rightmost point to leftmost point.
# For left arc (center at u=1): rightmost is (2,0), leftmost is (0,0). This is the upper half.
# For right arc (center at u=3.8): rightmost is (4.8,0), leftmost is (2.8,0). This is also upper half.
# But then the lines are at v=-1 (bottom) and v=1 (top).
#
# Actually, if both arcs are upper halves, the shape would be:
#   Start at (2,0), go along upper arc to (0,0), then line to (1,-1)? No, (0,0) to (1,-1) is not a line in the plan.
#
# I think the start/end angles might be defined differently. Let's assume the arcs go from bottom to top:
#   Left arc: from (1,-1) to (1,1) -> center (1,0), radius 1, start -90°, end 90°
#   Right arc: from (3.8,1) to (3.8,-1) -> center (3.8,0), radius 1, start 90°, end -90° (or 270°)
#   Top line: from (1,1) to (3.8,1)
#   Bottom line: from (3.8,-1) to (1,-1)
#
# This matches the line endpoints: Line1 from (1,-1) to (3.8,-1) is bottom line.
# Line2 from (3.8,1) to (1,1) is top line.
#
# So the arcs should be:
#   Left arc: center (1,0), radius 1, start 90°, end -90° (or 270°) going clockwise? 
#   Actually, to go from bottom (1,-1) to top (1,1) counterclockwise: start -90°, end 90°.
#   Right arc: center (3.8,0), radius 1, start 90°, end -90° (or 270°) going counterclockwise from top to bottom.
#
# But the plan says start_angle=0°, end_angle=180° for both. This might be a convention where 0° is at the top?
# Or the arcs are defined differently. Given the constraints (tangent, parallel), the shape is a valid stadium.
#
# To avoid confusion, I'll build the stadium directly using the dimensions: radius=10, straight_length=28.
# The stadium is centered along u with total length = 2*radius + straight_length = 48.
# The v span = 2*radius = 20.
#
# I'll create the profile in the XY plane, then rotate to match the frame (v_dir = -Z, w_dir = Y).
# The frame has: u=X, v=-Z, w=Y. So the profile is in the XZ plane (u=X, v=Z) but v is negated.
# Actually, we can build in XY and then rotate.

# Build stadium in XY plane (u=X, v=Y)
# Left semicircle center at (radius, 0) = (10, 0)
# Right semicircle center at (radius + straight_length, 0) = (38, 0)

# Create the profile using CadQuery's 2D primitives
# We'll use a workplane and build the stadium shape

result = (
    cq.Workplane("XY")
    .center(radius + straight_length/2, 0)  # center of stadium at (24, 0)
    .stadium(radius, straight_length)  # stadium(width=straight_length, height=2*radius)
    .extrude(4.0)  # extrude along Z (which will become Y after rotation? No, we need to orient)
)

# The stadium is built in XY plane and extruded in Z. But we need:
#   u_dir = X, v_dir = -Z, w_dir = Y
# So the profile should be in the XZ plane (u=X, v=Z) and extrude along Y (w).
# Since v_dir = -Z, we need to mirror the profile in Z.
#
# Let's build in XZ plane instead:

result = (
    cq.Workplane("XZ")
    .center(radius + straight_length/2, 0)  # center at (24, 0) in XZ
    .stadium(radius, straight_length)  # stadium in XZ plane
    .extrude(4.0)  # extrude along Y (positive Y)
)

# Now the stadium is oriented with:
#   u (X) = X axis
#   v (Z) = Z axis (but we need -Z, so we need to mirror)
#   w (Y) = Y axis
#
# To get v_dir = -Z, we can mirror about the XY plane (i.e., scale Z by -1).
# Or we can rotate 180 degrees about X axis.

# Mirror about XY plane (negate Z)
result = result.mirror("XY")

# Alternatively, we could have built the stadium with center at (24, 0) and then rotated.
# But mirror is simpler.

# The resulting shape should have:
#   span along X (u): 48 mm
#   span along Z (v): 20 mm (but mirrored, so from -10 to 10? Actually mirror doesn't change span)
#   span along Y (w): 4 mm

# Export
import cadquery as cq
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102295_86f842dd_0000\\neg_03/generated.step")
