import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0001\neg_02\iter_01\generated.step"

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

# Points for the outer profile:
p1 = (0.9188335453558412, 0.0)  # bottom-left
p2 = (3.8000000566244125, 0.0)  # bottom-right
p3 = (3.7174115708793822, 1.7936743887554851)  # top-right
p4 = (0.9188335453558412, 1.7936743887554851)  # top-left

# Center and radius of the outer arc
cx = 2.3181225581176115
cy = 1.7490620724718653
r = 1.4

# Inner hole parameters
inner_cx = 2.3181225581176115
inner_cy = 1.7490620724718653
inner_r = 1.25

# Build the outer profile using Workplane
wp = cq.Workplane("XY")

# Start at bottom-left
wp = wp.moveTo(p1[0], p1[1])
# Line to bottom-right
wp = wp.lineTo(p2[0], p2[1])
# Line to top-right
wp = wp.lineTo(p3[0], p3[1])

# Calculate the midpoint of the arc for threePointArc
v3 = cq.Vector(p3[0] - cx, p3[1] - cy, 0)
v4 = cq.Vector(p4[0] - cx, p4[1] - cy, 0)
angle3 = math.atan2(v3.y, v3.x)
angle4 = math.atan2(v4.y, v4.x)
if angle4 < angle3:
    angle4 += 2 * math.pi
mid_angle = (angle3 + angle4) / 2
mid_x = cx + r * math.cos(mid_angle)
mid_y = cy + r * math.sin(mid_angle)

# Arc to top-left
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
