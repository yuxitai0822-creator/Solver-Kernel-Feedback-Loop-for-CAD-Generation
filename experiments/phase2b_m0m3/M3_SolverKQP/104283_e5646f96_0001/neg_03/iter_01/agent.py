import math
import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0001\neg_03\iter_01/generated.step"

EXTENT_TOTAL_MM = 18.0

# Outer profile points (from design plan)
p1 = (0.9188335453558412, 0.0)
p2 = (3.8000000566244125, 0.0)
p3 = (3.7174115708793822, 1.7936743887554851)
p4 = (0.9188335453558412, 1.7936743887554851)

# Outer arc parameters
center_outer = (2.3181225581176115, 1.7490620724718653)
radius_outer = 1.4

# Compute angles for the arc from p3 to p4 (counterclockwise)
dx3 = p3[0] - center_outer[0]
dy3 = p3[1] - center_outer[1]
dx4 = p4[0] - center_outer[0]
dy4 = p4[1] - center_outer[1]
angle3 = math.atan2(dy3, dx3)
angle4 = math.atan2(dy4, dx4)
if angle4 < angle3:
    angle4 += 2 * math.pi

# Midpoint of the arc
mid_angle = (angle3 + angle4) / 2.0
mid_x = center_outer[0] + radius_outer * math.cos(mid_angle)
mid_y = center_outer[1] + radius_outer * math.sin(mid_angle)

# Build outer profile using Workplane
wp = cq.Workplane("XY")
wp = wp.moveTo(p1[0], p1[1])
wp = wp.lineTo(p2[0], p2[1])
wp = wp.lineTo(p3[0], p3[1])
wp = wp.threePointArc((mid_x, mid_y), (p4[0], p4[1]))
wp = wp.lineTo(p1[0], p1[1])
wp = wp.close()

# Extrude outer profile
result = wp.extrude(EXTENT_TOTAL_MM)

# Inner hole (circle)
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.25

cut_wp = cq.Workplane("XY").moveTo(inner_center[0], inner_center[1]).circle(inner_radius)
cut_prism = cut_wp.extrude(EXTENT_TOTAL_MM * 1.5)

result = result.cut(cut_prism)

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")