import json
import math
from pathlib import Path
import cadquery as cq
from cadquery import exporters

# ============================================================
# Design Plan Reconstruction for Untitled v1
# ============================================================
# This script builds the part from the design plan's solid_bodies
# description, using the explicit profile curves and extrude parameters.
# The part consists of a base profile (outer loop) with a concentric
# circular hole (inner loop), extruded 18.0 mm in +Z.
# ============================================================

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0001\neg_03\iter_00/generated.step"

# ---- Parameters from design plan ----
EXTENT_TOTAL_MM = 18.0  # extrude distance

# Profile 0: outer loop (composite line+arc)
# Curves (from design plan):
#   line: (0.9188335453558412, 1.7936743887554851) -> (0.9188335453558412, 0.0)
#   line: (0.9188335453558412, 0.0) -> (3.8000000566244125, 0.0)
#   line: (3.7174115708793822, 1.7936743887554851) -> (3.7174115708793822, 0.0)
#   circle: center (2.3181225581176115, 1.7490620724718653), radius 1.4
#
# Note: The circle is tangent to the top edge? Actually the circle center
# is at y=1.749, radius 1.4, so it extends from y=0.349 to y=3.149.
# The top line endpoints are at y=1.7937, so the circle protrudes above.
# We'll build the outer profile as a closed wire: start at bottom-left,
# go right along bottom, then up right side, then arc, then left along top.

# Profile 1: inner loop (circle)
#   circle: center (2.3181225581176115, 1.7490620724718653), radius 1.25

# ---- Build outer profile ----
# We'll construct the outer wire manually using edges.

# Points (scaled from design plan, already in mm)
p1 = (0.9188335453558412, 0.0)          # bottom-left
p2 = (3.8000000566244125, 0.0)          # bottom-right
p3 = (3.7174115708793822, 1.7936743887554851)  # top-right (slightly left of p2)
p4 = (0.9188335453558412, 1.7936743887554851)  # top-left

# Circle for outer arc (top edge is actually an arc of radius 1.4)
center_outer = (2.3181225581176115, 1.7490620724718653)
radius_outer = 1.4

# We need to find the arc that goes from p3 to p4 (or p4 to p3) with given center.
# The arc should be the one that bulges upward (since center y=1.749 < p3.y=1.7937? Actually center y is slightly lower, so arc goes upward).
# Let's compute angles:
import math
dx3 = p3[0] - center_outer[0]
dy3 = p3[1] - center_outer[1]
dx4 = p4[0] - center_outer[0]
dy4 = p4[1] - center_outer[1]
angle3 = math.atan2(dy3, dx3)
angle4 = math.atan2(dy4, dx4)
# We want the arc that goes from p3 to p4 in the positive (counterclockwise) direction.
# Since p3 is to the right and p4 to the left, the CCW arc goes through the top.
# Ensure angle4 > angle3 for CCW
if angle4 < angle3:
    angle4 += 2*math.pi

# Build the outer wire using CadQuery's WireBuilder or edge construction.
# We'll use a Workplane approach: create a polygon approximating the shape,
# then fillet? No, we need exact arc. Better: use cq.Workplane with three-point arc.

# Strategy: build the profile as a sketch using lines and arcs.
wp = cq.Workplane("XY")

# Start at p1 (bottom-left)
wp = wp.moveTo(p1[0], p1[1])
# Line to p2 (bottom-right)
wp = wp.lineTo(p2[0], p2[1])
# Line to p3 (right side, up)
wp = wp.lineTo(p3[0], p3[1])
# Arc from p3 to p4 (top edge, bulging upward)
# Use three-point arc: we need a point on the arc. The midpoint of the arc at angle halfway:
mid_angle = (angle3 + angle4) / 2.0
mid_x = center_outer[0] + radius_outer * math.cos(mid_angle)
mid_y = center_outer[1] + radius_outer * math.sin(mid_angle)
wp = wp.threePointArc(mid_x, mid_y, p4[0], p4[1])
# Line back to p1 (left side, down)
wp = wp.lineTo(p1[0], p1[1])
wp = wp.close()

# Extrude the outer profile
result = wp.extrude(EXTENT_TOTAL_MM)

# ---- Cut inner hole ----
# Inner circle
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.25

# Create a circle on the same workplane and extrude it as a cutting prism
cut_wp = cq.Workplane("XY").moveTo(inner_center[0], inner_center[1]).circle(inner_radius)
cut_prism = cut_wp.extrude(EXTENT_TOTAL_MM * 1.5)  # overshoot to ensure clean cut

result = result.cut(cut_prism)

# ---- Export ----
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
