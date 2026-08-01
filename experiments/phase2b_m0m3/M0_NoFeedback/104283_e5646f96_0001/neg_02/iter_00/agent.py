import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0001\neg_02\iter_00\generated.step"

# Design Plan interpretation:
# - Two profiles (outer rings) that share a common circle
# - Profile 1: rectangle with a circular arc on one side
# - Profile 2: rectangle with a circular arc on one side, plus an inner circle (hole)
# - Extrude 18.0 mm in +Z direction
# - The geometry is essentially a slotted shape with a hole

# Build the base shape (profile 1): a rectangle with a circular end
# Points from the design plan:
# Start at (0.9188335453558412, 1.7936743887554851) -> line down to (0.9188335453558412, 0.0)
# -> line to (3.8000000566244125, 0.0) -> line to (3.7174115708793822, 1.7936743887554851)
# -> circle center (2.3181225581176115, 1.7490620724718653) radius 1.4

# Create the first profile as a wire
wp = cq.Workplane("XY")

# Build the outer shape using polyline and arc
# Start at the top-left point
p1 = (0.9188335453558412, 1.7936743887554851)
p2 = (0.9188335453558412, 0.0)
p3 = (3.8000000566244125, 0.0)
p4 = (3.7174115708793822, 1.7936743887554851)
center = (2.3181225581176115, 1.7490620724718653)
radius = 1.4

# Build the wire manually
# Start at p1, line to p2, line to p3, line to p4, then arc back to p1
# The arc goes from p4 to p1 around the center
# Calculate angles for the arc
angle_p4 = math.atan2(p4[1] - center[1], p4[0] - center[0])
angle_p1 = math.atan2(p1[1] - center[1], p1[0] - center[0])

# Ensure the arc goes the right way (counterclockwise)
if angle_p1 < angle_p4:
    angle_p1 += 2 * math.pi

# Create the wire using polyline and three-point arc
# Use a workplane approach: move to start, then lineTo, then threePointArc
wp = wp.moveTo(p1[0], p1[1])
wp = wp.lineTo(p2[0], p2[1])
wp = wp.lineTo(p3[0], p3[1])
wp = wp.lineTo(p4[0], p4[1])

# Now add the arc from p4 back to p1
# For threePointArc, we need a midpoint on the arc
mid_angle = (angle_p4 + angle_p1) / 2
mid_point = (center[0] + radius * math.cos(mid_angle), center[1] + radius * math.sin(mid_angle))
wp = wp.threePointArc(mid_point, p1)
wp = wp.close()

# Extrude the base shape
result = wp.extrude(18.0)

# Now cut the inner hole (profile 2 inner ring)
# Inner circle center (2.3181225581176115, 1.7490620724718653) radius 1.25
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.2500000000000002

# Create a circle for the hole
hole_wp = cq.Workplane("XY").moveTo(inner_center[0], inner_center[1]).circle(inner_radius)
hole = hole_wp.extrude(18.0)

# Cut the hole from the result
result = result.cut(hole)

# Export
exporters.export(result, OUT_STEP_PATH)
