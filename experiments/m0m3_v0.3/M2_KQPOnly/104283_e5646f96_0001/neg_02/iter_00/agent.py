import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0001\neg_02\iter_00\generated.step"

# Design parameters from the design plan
# The profile consists of:
# - Outer shape: a rectangle with a circular arc on one side
# - Inner hole: a circle
# All dimensions are in mm (converted from cm where needed)

# From the design plan curves:
# Outer loop curves:
# 1. Line from (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
# 2. Line from (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
# 3. Line from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
# 4. Circle at center (2.3181225581176115, 1.7490620724718653) radius 1.4
#
# Inner loop (hole):
# - Circle at center (2.3181225581176115, 1.7490620724718653) radius 1.25
#
# Extrude distance: 18.0 mm

# Build the outer profile
# The outer shape is a rectangle with a circular arc on top
# Rectangle width: from x=0.9188 to x=3.8000 (or 3.7174)
# Rectangle height: from y=0 to y=1.7937
# The circle arc connects the two vertical lines at the top

# Let's build this as a 2D sketch then extrude

# Create the outer profile using a wire
# We'll use the points from the design plan

# Points for the outer profile:
# Start at bottom-left: (0.9188335453558412, 0.0)
# Go to bottom-right: (3.8000000566244125, 0.0)
# Go to top-right: (3.7174115708793822, 1.7936743887554851)
# Arc to top-left: (0.9188335453558412, 1.7936743887554851)
# Close back to start

# The arc is a circle centered at (2.3181225581176115, 1.7490620724718653) with radius 1.4
# This circle passes through both top points

# Build the outer profile
wp = cq.Workplane("XY")

# Start with the outer shape
# We'll create a closed wire using the points and arc

# First, create the points for the straight segments
p1 = (0.9188335453558412, 0.0)  # bottom-left
p2 = (3.8000000566244125, 0.0)  # bottom-right
p3 = (3.7174115708793822, 1.7936743887554851)  # top-right
p4 = (0.9188335453558412, 1.7936743887554851)  # top-left

# Center of the arc
cx = 2.3181225581176115
cy = 1.7490620724718653
r = 1.4

# Create the outer wire using a polyline and arc
# We'll use the approach of creating edges and combining them

# Create the bottom edge
edge1 = cq.Edge.makeLine(cq.Vector(p1[0], p1[1], 0), cq.Vector(p2[0], p2[1], 0))

# Create the right vertical edge
edge2 = cq.Edge.makeLine(cq.Vector(p2[0], p2[1], 0), cq.Vector(p3[0], p3[1], 0))

# Create the arc from p3 to p4
# The arc is part of a circle centered at (cx, cy) with radius r
# We need to find the angles
v3 = cq.Vector(p3[0] - cx, p3[1] - cy, 0)
v4 = cq.Vector(p4[0] - cx, p4[1] - cy, 0)
angle3 = math.atan2(v3.y, v3.x)
angle4 = math.atan2(v4.y, v4.x)
# Ensure we go the right way (counterclockwise from p3 to p4)
if angle4 < angle3:
    angle4 += 2 * math.pi

# Create the arc
edge3 = cq.Edge.makeCircle(r, cq.Vector(cx, cy, 0), cq.Vector(0, 0, 1), angle3, angle4)

# Create the left vertical edge
edge4 = cq.Edge.makeLine(cq.Vector(p4[0], p4[1], 0), cq.Vector(p1[0], p1[1], 0))

# Combine edges into a wire
wire = cq.Wire.combine([edge1, edge2, edge3, edge4])

# Create a face from the wire
outer_face = cq.Face.makeFromWires(wire)

# Now create the inner hole (circle)
inner_cx = 2.3181225581176115
inner_cy = 1.7490620724718653
inner_r = 1.25

inner_circle = cq.Wire.makeCircle(inner_r, cq.Vector(inner_cx, inner_cy, 0), cq.Vector(0, 0, 1))
inner_face_hole = cq.Face.makeFromWires(inner_circle)

# Cut the hole from the outer face
# We need to create a compound face with the hole
# Using the cut operation on faces

# Alternative approach: use Workplane operations
# Create the outer shape as a workplane object

# Let's use a simpler approach with Workplane
wp = cq.Workplane("XY")

# Create the outer profile using polyline and arc
# We'll use the three-point arc method

# Build the outer shape
# Start at bottom-left
wp = wp.moveTo(p1[0], p1[1])
# Line to bottom-right
wp = wp.lineTo(p2[0], p2[1])
# Line to top-right
wp = wp.lineTo(p3[0], p3[1])
# Arc to top-left (three-point arc: start=p3, mid=top of circle, end=p4)
# The midpoint of the arc is at the top of the circle
mid_angle = (angle3 + angle4) / 2
mid_x = cx + r * math.cos(mid_angle)
mid_y = cy + r * math.sin(mid_angle)
wp = wp.threePointArc(cq.Vector(mid_x, mid_y, 0), cq.Vector(p4[0], p4[1], 0))
# Line back to start
wp = wp.lineTo(p1[0], p1[1])
wp = wp.close()

# Extrude the outer shape
result = wp.extrude(18.0)

# Now cut the inner hole
# Create the inner circle as a cutting tool
inner_wp = cq.Workplane("XY").moveTo(inner_cx, inner_cy).circle(inner_r)
inner_cut = inner_wp.extrude(18.0)

# Cut the hole
result = result.cut(inner_cut)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
