import cadquery as cq
from cadquery import exporters
import math

# Design Plan interpretation:
# - Two profiles (outer rings) that share a common circle
# - Profile 1: rectangle with a circular cutout (inner circle)
# - Profile 2: the same circle as outer, with a smaller inner circle
# - Extrude 18.0 mm (not 27.0 mm from previous script)
# - The perturbation changed extrude depth from 1.8 cm to 2.7 cm, but design plan says 18.0 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0001\neg_01\iter_00/generated.step"

# Build the base shape: a rectangle with a circular protrusion
# From the design plan profiles:
# Profile 1: rectangle from (0.9188, 0) to (3.7174, 1.7937) with a circle at (2.3181, 1.7491) radius 1.4
# Profile 2: circle at (2.3181, 1.7491) radius 1.4 with inner circle radius 1.25

# The combined shape is a rectangle with a circular extension on top
# Let's build it as a single sketch with proper geometry

# Create the workplane
wp = cq.Workplane("XY")

# Build the outer profile: rectangle with circular top
# Start with the rectangle part
pts = [
    (0.9188335453558412, 0.0),
    (3.8000000566244125, 0.0),
    (3.7174115708793822, 1.7936743887554851),
    (0.9188335453558412, 1.7936743887554851),
]

# Create the base rectangle
base = wp.moveTo(pts[0][0], pts[0][1]).lineTo(pts[1][0], pts[1][1]).lineTo(pts[2][0], pts[2][1]).lineTo(pts[3][0], pts[3][1]).close()

# Add the circle (outer circle of profile 2)
# The circle center is at (2.3181225581176115, 1.7490620724718653) with radius 1.4
# But this circle overlaps with the rectangle, so we need to union them
# Better approach: create the circle separately and union

# Actually, let's re-think: The design plan shows two profiles that are extruded together
# Profile 1: rectangle with a circular cutout (inner circle radius 1.25)
# Profile 2: circle (radius 1.4) with inner circle (radius 1.25)
# The combined shape is a rectangle with a circular bump on top, with a through hole

# Let's build it step by step:
# 1. Create the rectangle
# 2. Create the outer circle
# 3. Union them
# 4. Cut the inner circle (through hole)

# Step 1: Rectangle
rect = cq.Workplane("XY").moveTo(0.9188335453558412, 0.0).lineTo(3.8000000566244125, 0.0).lineTo(3.7174115708793822, 1.7936743887554851).lineTo(0.9188335453558412, 1.7936743887554851).close()

# Step 2: Outer circle
circle_outer = cq.Workplane("XY").moveTo(2.3181225581176115, 1.7490620724718653).circle(1.4)

# Step 3: Union (combine rectangle and circle)
# We need to create wires and make a compound face
# Actually, let's use a simpler approach: create the shape as a single wire

# The combined outer boundary is:
# Start at bottom-left of rectangle
# Go right to bottom-right
# Go up to top-right (but this is inside the circle, so we follow the circle arc)
# Actually, the circle center is at y=1.749, radius 1.4, so the circle extends from y=0.349 to y=3.149
# The rectangle top is at y=1.794, which is inside the circle
# So the combined shape is: rectangle from y=0 to y=1.794, plus circle from y=1.794 to y=3.149

# Let's build the combined outer wire properly
# We'll use a polyline approximation for the circle arc

# Points for the combined shape:
# Start at (0.9188, 0) - bottom left of rectangle
# Go to (3.8000, 0) - bottom right of rectangle
# Go to (3.7174, 1.7937) - top right of rectangle (where it meets the circle)
# Follow circle arc from (3.7174, 1.7937) around to (0.9188, 1.7937)
# Close back to start

# The circle center is at (2.3181, 1.7491), radius 1.4
# The intersection points with the rectangle top edge (y=1.7937):
# (x - 2.3181)^2 + (1.7937 - 1.7491)^2 = 1.4^2
# (x - 2.3181)^2 + 0.0446^2 = 1.96
# (x - 2.3181)^2 = 1.96 - 0.00199 = 1.958
# x - 2.3181 = ±1.3993
# x = 3.7174 or x = 0.9188
# So the rectangle top edge exactly touches the circle at these points!

# This means the combined shape is simply the circle with a rectangular tab below it
# The outer boundary is:
# - Circle arc from (3.7174, 1.7937) going counterclockwise to (0.9188, 1.7937)
# - Line from (0.9188, 1.7937) down to (0.9188, 0)
# - Line from (0.9188, 0) to (3.8000, 0)
# - Line from (3.8000, 0) up to (3.7174, 1.7937)

# Let's build this wire
# Circle arc: from angle at (3.7174, 1.7937) to angle at (0.9188, 1.7937)
# Angle of (3.7174, 1.7937) relative to center: atan2(1.7937-1.7491, 3.7174-2.3181) = atan2(0.0446, 1.3993) ≈ 0.0319 rad
# Angle of (0.9188, 1.7937) relative to center: atan2(1.7937-1.7491, 0.9188-2.3181) = atan2(0.0446, -1.3993) ≈ π - 0.0319 ≈ 3.1097 rad

# So the arc goes from angle 0.0319 to 3.1097 (counterclockwise)
# That's about 177 degrees

# Let's discretize the arc
center_x, center_y = 2.3181225581176115, 1.7490620724718653
radius = 1.4
start_angle = math.atan2(1.7936743887554851 - center_y, 3.7174115708793822 - center_x)
end_angle = math.atan2(1.7936743887554851 - center_y, 0.9188335453558412 - center_x)

# Ensure counterclockwise (end_angle > start_angle)
if end_angle < start_angle:
    end_angle += 2 * math.pi

# Build the outer wire
wp_outer = cq.Workplane("XY")

# Start at bottom-left
wp_outer = wp_outer.moveTo(0.9188335453558412, 0.0)
# Line to bottom-right
wp_outer = wp_outer.lineTo(3.8000000566244125, 0.0)
# Line to top-right (circle intersection)
wp_outer = wp_outer.lineTo(3.7174115708793822, 1.7936743887554851)
# Arc along circle to top-left (circle intersection)
# Discretize the arc
N = 64
for i in range(1, N + 1):
    t = start_angle + (end_angle - start_angle) * (i / N)
    px = center_x + radius * math.cos(t)
    py = center_y + radius * math.sin(t)
    wp_outer = wp_outer.lineTo(px, py)
# Close back to start
wp_outer = wp_outer.close()

# Now create the inner hole (circle radius 1.25)
wp_inner = cq.Workplane("XY").moveTo(center_x, center_y).circle(1.2500000000000002)

# Extrude the outer shape
result = wp_outer.extrude(18.0)

# Cut the inner hole
cut_prism = wp_inner.extrude(18.0 * 1.5)
result = result.cut(cut_prism)

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")