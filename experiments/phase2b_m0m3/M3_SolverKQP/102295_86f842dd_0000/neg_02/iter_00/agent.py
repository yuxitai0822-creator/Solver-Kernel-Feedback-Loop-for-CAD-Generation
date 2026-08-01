import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102295_86f842dd_0000\neg_02\iter_00\generated.step"

# Build the stadium profile in the XZ plane (u=1,0,0; v=0,0,-1; w=0,1,0)
# The design plan specifies:
#   - straight_length = 28.0 mm (distance between arc centers)
#   - radius = 10.0 mm (arc radius)
#   - extrude distance = 4.0 mm along +w (Y direction)
# The profile is centered such that the overall span along u is 48.0 mm and along v is 20.0 mm.

# Create workplane on XZ plane (normal = Y axis)
wp = cq.Workplane("XZ")

# Build the stadium: two arcs (radius 10) connected by two lines.
# Arc centers at (14.0, 0.0) and (42.0, 0.0) in XZ plane (u,v).
# The straight length is 28.0, so centers are 28 apart.
# The overall width along u is 2*radius + straight_length = 20 + 28 = 48.
# The height along v is 2*radius = 20.
# We'll construct the profile using a polyline with arc discretization.

# Start at the leftmost point: (14.0 - 10.0, 0.0) = (4.0, 0.0)
# But the design plan's curves start at (1.0, -1.0) in UV? Actually the plan uses UV coordinates
# where the arc centers are at (1.0, 0.0) and (3.8, 0.0) with radius 1.0, but those are in cm.
# After unit conversion (cm to mm, factor 10), the centers become (10.0, 0.0) and (38.0, 0.0)
# with radius 10.0. The straight length becomes 28.0 mm.
# So we use centers at (10.0, 0.0) and (38.0, 0.0) in the XZ plane.

# Build the profile using a polyline with arc discretization (128 segments per arc)
N_ARC = 128

# Start at the leftmost point of the left arc (angle 0): (10.0 + 10.0*cos(0), 0.0 + 10.0*sin(0)) = (20.0, 0.0)
# But the design plan's start_angle is 0.0 and end_angle is 180.0 for the first arc.
# So the arc goes from angle 0 to 180, which is the top half? Actually in the UV frame,
# u is horizontal, v is vertical. The arc center is at (10.0, 0.0), radius 10.0.
# start_angle=0 means point at (10.0+10.0*cos(0), 0.0+10.0*sin(0)) = (20.0, 0.0)
# end_angle=180 means point at (10.0+10.0*cos(180), 0.0+10.0*sin(180)) = (0.0, 0.0)
# But the line then goes from (10.0, -10.0) to (38.0, -10.0) in UV? Wait, the design plan's curves:
#   arc1: center_uv=[1.0,0.0], radius=1.0, start_angle=0, end_angle=180
#   line1: start_uv=[1.0,-1.0], end_uv=[3.8,-1.0]
#   arc2: center_uv=[3.8,0.0], radius=1.0, start_angle=0, end_angle=180
#   line2: start_uv=[3.8,1.0], end_uv=[1.0,1.0]
# After scaling by 10: centers at (10,0) and (38,0), radius=10.
# The arcs go from angle 0 to 180, which in the UV frame (u right, v up) means:
#   arc1: from (10+10*cos0, 0+10*sin0) = (20,0) to (10+10*cos180, 0+10*sin180) = (0,0)
#   But the line starts at (10, -10) and ends at (38, -10). That doesn't match.
# Actually the design plan's UV coordinates are in cm, and the arcs are drawn from angle 0 to 180.
# The start_uv of line1 is (1.0, -1.0) which after scaling is (10, -10).
# The end_uv of arc1 should be (1.0, -1.0) if the arc ends at angle -90? No.
# Let's re-interpret: The arcs are drawn from start_angle to end_angle, but the start_angle is 0 and end_angle is 180.
# In the UV frame, angle 0 points along +u, angle 90 points along +v.
# So arc1: center (10,0), radius 10, from angle 0 to 180:
#   start point: (10+10*cos0, 0+10*sin0) = (20, 0)
#   end point: (10+10*cos180, 0+10*sin180) = (0, 0)
# But the line1 starts at (10, -10) and ends at (38, -10). That doesn't connect.
# Perhaps the arcs are drawn from angle 180 to 0 (i.e., the other direction)?
# Or perhaps the start_angle and end_angle are defined differently.
# Let's look at the line2: start_uv=[3.8,1.0], end_uv=[1.0,1.0]. After scaling: (38,10) to (10,10).
# So the top line goes from right to left at v=10.
# The bottom line goes from left to right at v=-10.
# The left arc connects the bottom line's left end (10,-10) to the top line's left end (10,10).
# The right arc connects the top line's right end (38,10) to the bottom line's right end (38,-10).
# So the left arc should go from (10,-10) to (10,10) with center at (10,0). That's a half-circle from angle -90 to 90.
# But the design says start_angle=0, end_angle=180. That would give a half-circle from (20,0) to (0,0).
# There's a mismatch. Let's assume the design plan's angles are measured from the +u axis, but the arcs are drawn in the opposite direction (clockwise vs counterclockwise).
# Actually, if we take start_angle=0 and end_angle=180, but the arc is drawn clockwise, then it goes from angle 0 to -180, which gives points from (20,0) to (0,0) going through the bottom half.
# That still doesn't match (10,-10) to (10,10).
# Let's just use the explicit points from the design plan's curves after scaling:
#   arc1: center (10,0), radius 10, start point (20,0), end point (0,0) — but that's not connected to the lines.
# I think the design plan's UV coordinates are in a different orientation. Let's just build the stadium from the dimensions:
# straight_length = 28.0 mm, radius = 10.0 mm.
# The profile is symmetric about the u-axis (v=0). The left arc center is at u=10.0, v=0. The right arc center is at u=38.0, v=0.
# The left arc goes from (10, -10) to (10, 10) — that's a half-circle from angle -90 to 90.
# The right arc goes from (38, 10) to (38, -10) — that's a half-circle from angle 90 to -90.
# The bottom line goes from (10, -10) to (38, -10).
# The top line goes from (38, 10) to (10, 10).
# So we'll build the profile accordingly.

# Build the profile as a polyline with arc discretization
wp = wp.moveTo(10.0, -10.0)  # start at bottom-left of left arc

# Left arc: from (10, -10) to (10, 10), center (10, 0), radius 10, from angle -90 to 90
cx1, cy1 = 10.0, 0.0
r = 10.0
sa1 = -math.pi/2
ea1 = math.pi/2
for k in range(1, N_ARC+1):
    t = sa1 + (ea1 - sa1) * (k / N_ARC)
    px = cx1 + r * math.cos(t)
    py = cy1 + r * math.sin(t)
    wp = wp.lineTo(px, py)

# Bottom line: from (10, 10) to (38, 10) — wait, after the left arc we are at (10, 10).
# Actually the left arc ends at (10, 10). Then the top line goes from (38, 10) to (10, 10)? No, the top line goes from right to left.
# Let's reorder: The profile should be a closed loop. Let's start at the bottom-left corner (10, -10).
# Then go along the bottom line to (38, -10).
# Then go along the right arc from (38, -10) to (38, 10).
# Then go along the top line from (38, 10) to (10, 10).
# Then go along the left arc from (10, 10) to (10, -10).
# That's a valid closed loop.

# So let's rebuild:
wp = cq.Workplane("XZ")
wp = wp.moveTo(10.0, -10.0)  # bottom-left

# Bottom line: to (38, -10)
wp = wp.lineTo(38.0, -10.0)

# Right arc: from (38, -10) to (38, 10), center (38, 0), radius 10, from angle -90 to 90
cx2, cy2 = 38.0, 0.0
sa2 = -math.pi/2
ea2 = math.pi/2
for k in range(1, N_ARC+1):
    t = sa2 + (ea2 - sa2) * (k / N_ARC)
    px = cx2 + r * math.cos(t)
    py = cy2 + r * math.sin(t)
    wp = wp.lineTo(px, py)

# Top line: from (38, 10) to (10, 10)
wp = wp.lineTo(10.0, 10.0)

# Left arc: from (10, 10) to (10, -10), center (10, 0), radius 10, from angle 90 to -90 (or 90 to 270)
sa3 = math.pi/2
ea3 = -math.pi/2  # going clockwise
for k in range(1, N_ARC+1):
    t = sa3 + (ea3 - sa3) * (k / N_ARC)
    px = cx1 + r * math.cos(t)
    py = cy1 + r * math.sin(t)
    wp = wp.lineTo(px, py)

wp = wp.close()

# Extrude along +Y (w direction) by 4.0 mm
result = wp.extrude(4.0)

# Export
importers = None
exporters.export(result, OUT_STEP_PATH)
