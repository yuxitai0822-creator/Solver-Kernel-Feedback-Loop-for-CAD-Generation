import cadquery as cq
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0001\neg_01\iter_01\generated.step"

# Design Plan interpretation:
# - Two profiles (outer rings) that share a common circle
# - Profile 1: rectangle with a circular arc at the top
# - Profile 2: rectangle with a circular arc at the top, with an inner circle (hole)
# - Extrude 18.0 mm in +Z direction
# - The geometry is a flat plate with a circular boss and a through hole

# Build the base profile (outer shape)
# The outer shape consists of:
# - Left vertical line from (0.9188, 0) to (0.9188, 1.7937)
# - Bottom horizontal line from (0.9188, 0) to (3.8000, 0)
# - Right vertical line from (3.7174, 0) to (3.7174, 1.7937)
# - Circular arc at top connecting the two vertical lines

# Create the outer wire
wp = cq.Workplane("XY")

# Build the outer profile using points
# Start at bottom-left corner
p1 = (0.9188335453558412, 0.0)
p2 = (3.8000000566244125, 0.0)
p3 = (3.7174115708793822, 1.7936743887554851)
p4 = (0.9188335453558412, 1.7936743887554851)

# The top is a circular arc with center at (2.3181225581176115, 1.7490620724718653), radius 1.4
center = (2.3181225581176115, 1.7490620724718653)
radius = 1.4

# Create the outer wire using polyline and arc
# Start at p1, go to p2 (bottom edge)
# Then to p3 (right edge)
# Then arc from p3 to p4
# Then back to p1 (left edge)

# Use a workplane approach: create the sketch with lines and arc
wp = wp.moveTo(p1[0], p1[1])
wp = wp.lineTo(p2[0], p2[1])
wp = wp.lineTo(p3[0], p3[1])

# Add the arc from p3 to p4
# Calculate angles for the arc
start_angle = math.degrees(math.atan2(p3[1] - center[1], p3[0] - center[0]))
end_angle = math.degrees(math.atan2(p4[1] - center[1], p4[0] - center[0]))

# Use three-point arc through the top of the circle
# The top point of the circle is at (center[0], center[1] + radius)
top_point = (center[0], center[1] + radius)
wp = wp.threePointArc(p3, top_point, p4)

wp = wp.lineTo(p1[0], p1[1])
wp = wp.close()

# Extrude the outer profile
result = wp.extrude(18.0)

# Now create the inner hole (circle at center with radius 1.25)
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.2500000000000002

# Cut the inner hole
hole_wp = cq.Workplane("XY").moveTo(inner_center[0], inner_center[1]).circle(inner_radius)
hole = hole_wp.extrude(18.0)
result = result.cut(hole)

cq.exporters.export(result, OUT_STEP_PATH)