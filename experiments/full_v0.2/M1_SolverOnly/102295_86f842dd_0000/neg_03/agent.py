import cadquery as cq

# Design Plan: stadium extrusion
# Dimensions:
#   straight_length = 28.0 mm (inferred from point span)
#   radius = 10.0 mm (explicit)
#   extrude distance = 4.0 mm
#
# The stadium profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so positive v goes into -Z)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The profile curves (in UV coordinates):
#   Arc1: center (1.0, 0.0), radius 1.0, start 0°, end 180°
#   Line1: (1.0, -1.0) to (3.8, -1.0)
#   Arc2: center (3.8, 0.0), radius 1.0, start 0°, end 180°
#   Line2: (3.8, 1.0) to (1.0, 1.0)
#
# The UV coordinates are scaled by the actual dimensions:
#   radius = 10 mm -> scale factor = 10.0 (since radius in UV is 1.0)
#   straight_length = 28 mm -> the straight portion in UV is (3.8 - 1.0) = 2.8, scaled by 10 gives 28 mm
#
# After scaling, the stadium in XY plane (since u->X, v->-Z):
#   Arc1: center (10, 0) in XZ? Actually v is -Z, so we need to map carefully.
#   Let's build the profile in the XY plane (X = u, Y = -v) then extrude in Z.
#   Actually simpler: build in XY plane with X = u, Y = -v (since v_dir = (0,0,-1)).
#   Then extrude in +w = +Y direction.

# Build the stadium profile in XY plane
# Scaled dimensions:
R = 10.0  # radius
L = 28.0  # straight length
# The UV coordinates: arc centers at u=1.0 and u=3.8, radius 1.0
# Scale factor = 10
center1_x = 1.0 * R  # 10.0
center2_x = 3.8 * R  # 38.0
# The straight portion length in UV = 2.8, scaled = 28.0 (matches L)
# The half-height in UV = 1.0, scaled = 10.0 = R

# Build using CadQuery's workplane
# We'll create the profile by combining arcs and lines
# Start with the left arc (center at (10, 0), radius 10, from 180° to 0° going clockwise?)
# Actually in UV: arc from angle 0 to 180 (counterclockwise). 
# In XY plane: center (10,0), start at angle 0 (point (20,0)), end at angle 180 (point (0,0))
# But the line goes from (10, -10) to (38, -10) in UV? Wait:
#   Line1 start_uv = (1.0, -1.0) -> scaled (10, -10)
#   Line1 end_uv = (3.8, -1.0) -> scaled (38, -10)
# So the bottom line is at y = -10, from x=10 to x=38.
# The right arc: center (38, 0), radius 10, from 0 to 180 -> start (48,0), end (28,0)? 
#   Actually angle 0 is (center_x + R, 0) = (48,0), angle 180 is (center_x - R, 0) = (28,0)
# The top line: from (38, 10) to (10, 10)
# So the profile goes: start at (20,0) [left arc start], arc to (0,0) [left arc end], 
#   line to (38, -10)? No, that doesn't match.
# Let's re-express the UV curves in XY:
#   Arc1: center (10, 0), radius 10, start_angle=0°, end_angle=180°
#     In UV: start at (10+10*cos0, 0+10*sin0) = (20, 0)
#     end at (10+10*cos180, 0+10*sin180) = (0, 0)
#     This arc goes counterclockwise from (20,0) to (0,0) through the upper half (positive v)
#     But v is -Z, so positive v is negative Z. In XY plane, we map v to -Y, so positive v becomes negative Y.
#     Actually let's just build in XY with Y = -v, so the arc goes through negative Y.
#   Line1: from (10, -10) to (38, -10) in UV -> in XY: (10, 10) to (38, 10) because Y = -v
#   Arc2: center (38, 0), radius 10, start_angle=0°, end_angle=180°
#     start: (48, 0), end: (28, 0) in UV -> in XY: (48, 0) to (28, 0) (Y=0)
#     This arc goes through positive v (negative Y) in XY.
#   Line2: from (38, 1) to (1, 1) in UV -> in XY: (38, -1) to (1, -1) scaled: (38, -10) to (10, -10)
#
# So the profile in XY (scaled by 10):
#   Start at (20, 0)
#   Arc to (0, 0) with center (10, 0), going through negative Y (clockwise?)
#   Line to (38, 10)  [from (0,0) to (38,10)? No, line from (10,10) to (38,10)]
# Wait, let's trace carefully:
#   After Arc1, we are at (0,0). Then Line1 goes from (10, -10) to (38, -10) in UV.
#   But (0,0) is not (10,-10). There's a gap? No, the arc ends at (0,0) which is (1.0, 0.0) in UV? 
#   Actually arc1 end_uv = (1.0, 0.0) after scaling? No, arc1 end is at angle 180: (center_x - R, 0) = (0,0).
#   But line1 start is (1.0, -1.0) scaled = (10, -10). These are different points!
#   I think I mis-read the UV coordinates. Let's check the design plan again:
#   Arc1: center_uv = [1.0, 0.0], radius 1.0, start_angle=0, end_angle=180
#     start_uv = (1.0+1.0*cos0, 0+1.0*sin0) = (2.0, 0.0)
#     end_uv = (1.0+1.0*cos180, 0+1.0*sin180) = (0.0, 0.0)
#   Line1: start_uv = [1.0, -1.0], end_uv = [3.8, -1.0]
#   Arc2: center_uv = [3.8, 0.0], radius 1.0, start_angle=0, end_angle=180
#     start_uv = (4.8, 0.0), end_uv = (2.8, 0.0)
#   Line2: start_uv = [3.8, 1.0], end_uv = [1.0, 1.0]
#
# So the profile is:
#   Arc1 from (2.0, 0.0) to (0.0, 0.0) through upper half (positive v)
#   Line1 from (1.0, -1.0) to (3.8, -1.0)  -- but wait, arc1 ends at (0,0), line1 starts at (1,-1). Not connected!
#   This is confusing. Let's look at the order: curves are listed in order, they should form a closed loop.
#   Arc1: (2,0) -> (0,0)  (through positive v)
#   Line1: (1,-1) -> (3.8,-1)  -- but (0,0) != (1,-1). Something is off.
#   Maybe the UV coordinates are not the actual points but the parameterization?
#   Actually, looking at the dimensions: straight_length = 28, radius = 10.
#   The total width = 2*radius + straight_length = 20 + 28 = 48.
#   The total height = 2*radius = 20.
#   In UV, the width spans from 0 to 4.8 (since arc1 center at 1, arc2 center at 3.8, radius 1, so min x=0, max x=4.8).
#   Scaled by 10 gives 48. Height spans from -1 to 1 in UV, scaled gives 20.
#   So the profile in UV is a stadium with corners at (0,0), (4.8,0), (4.8,1), (0,1)? No, that's a rectangle.
#   Actually a stadium has straight sides and semicircular ends.
#   The left end is a semicircle from (0,0) to (2,0) with center (1,0), radius 1.
#   The right end is a semicircle from (2.8,0) to (4.8,0) with center (3.8,0), radius 1.
#   The top straight is from (2,0) to (2.8,0)? No, that's the top of the semicircles.
#   Actually the straight sides are at v=1 and v=-1, connecting the arcs.
#   So the loop should be:
#     Arc1: from (2,0) to (0,0) through v>0 (top semicircle of left end)
#     Line1: from (0,0) to (0, -1)? No, that would be a vertical line.
#   I think the UV coordinates in the design plan are not the actual curve endpoints but the control points.
#   Let's just build the stadium from the dimensions: radius=10, straight_length=28.
#   The stadium in XY plane (centered at origin for convenience):
#     Left semicircle: center at (-14, 0), radius 10, from 90° to -90° (or 270°)
#     Right semicircle: center at (14, 0), radius 10, from -90° to 90°
#     Top line: from (-14, 10) to (14, 10)
#     Bottom line: from (14, -10) to (-14, -10)
#   Total width = 28 + 20 = 48, total height = 20.
#   This matches the expected spans: u_span=48, v_span=20.

# Build using CadQuery
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(-14, 10)  # start at top-left of straight section
    .threePointArc((0, 20), (14, 10))  # right semicircle? No, this goes up.
    # Actually let's use a simpler approach: build the profile with lines and arcs
)

# Better approach: use the stadium shape directly
# We'll create a wire from the profile
from math import pi, sin, cos

# Build the profile points
R = 10.0
L = 28.0
half_L = L / 2.0  # 14.0

# Create the stadium profile as a CadQuery wire
# Start at the top-left corner of the straight section: (-half_L, R) = (-14, 10)
# Go right along top line to (half_L, R) = (14, 10)
# Then arc to (half_L, -R) = (14, -10) (right semicircle)
# Then left along bottom line to (-half_L, -R) = (-14, -10)
# Then arc to (-half_L, R) = (-14, 10) (left semicircle)

# Use CadQuery's wire construction
pts = [
    (-half_L, R),   # top-left
    (half_L, R),    # top-right
    (half_L, -R),   # bottom-right
    (-half_L, -R),  # bottom-left
]

# Build the stadium using a polyline and arcs
# Actually, let's use the workplane to create the shape
result = (
    cq.Workplane("XY")
    .moveTo(-half_L, R)  # start at top-left
    .lineTo(half_L, R)   # top edge
    .threePointArc((half_L + R, 0), (half_L, -R))  # right semicircle
    .lineTo(-half_L, -R)  # bottom edge
    .threePointArc((-half_L - R, 0), (-half_L, R))  # left semicircle
    .close()
    .extrude(4.0)  # extrude in +Z direction (since w_dir = (0,1,0) but we're in XY, extrude in Z)
)

# Note: The design plan says w_dir = (0,1,0) which is Y axis.
# But we built in XY plane and extruded in Z. 
# To match the frame: u_dir = X, v_dir = -Z, w_dir = Y.
# Our profile is in XY plane (X = u, Y = -v). Extruding in Z would give w = Z, not Y.
# We need to extrude in Y direction.
# Let's rebuild with the profile in XZ plane and extrude in Y.

# Rebuild: profile in XZ plane (X = u, Z = -v), extrude in Y
result = (
    cq.Workplane("XZ")
    .moveTo(-half_L, R)  # start at top-left (X, Z) where Z = -v, so positive v is negative Z
    .lineTo(half_L, R)   # top edge (in XZ, this is at Z = R)
    .threePointArc((half_L + R, 0), (half_L, -R))  # right semicircle
    .lineTo(-half_L, -R)  # bottom edge
    .threePointArc((-half_L - R, 0), (-half_L, R))  # left semicircle
    .close()
    .extrude(4.0)  # extrude in Y direction (perpendicular to XZ plane)
)

# Check: The profile in XZ plane:
#   Top edge at Z = R = 10 (which corresponds to v = -10, since v_dir = -Z)
#   Bottom edge at Z = -R = -10 (v = 10)
#   Left semicircle: center at (-14, 0), radius 10, from Z=10 to Z=-10 through X negative
#   Right semicircle: center at (14, 0), radius 10, from Z=-10 to Z=10 through X positive
# This matches the expected shape.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102295_86f842dd_0000\neg_03/generated.step")