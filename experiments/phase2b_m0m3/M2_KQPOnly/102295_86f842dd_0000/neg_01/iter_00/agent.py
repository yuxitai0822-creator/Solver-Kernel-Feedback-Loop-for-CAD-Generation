import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_01\iter_00\generated.step"

# Design parameters from the design plan
# Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
# Extrude distance = 4.0 mm (as per design plan, not the perturbed value)
straight_length = 28.0
radius = 10.0
extrude_distance = 4.0

# Build the stadium profile on the XZ plane (as per the original script's WORKPLANE = 'XZ')
# The profile is centered at the origin for simplicity
# Stadium consists of:
# - Left arc centered at (radius, 0) with radius, from 90° to 270° (or 0 to 180 in the plan's local UV)
# - Top line from (radius, radius) to (radius + straight_length, radius)
# - Right arc centered at (radius + straight_length, 0) with radius, from 270° to 90° (or 0 to 180)
# - Bottom line from (radius + straight_length, -radius) to (radius, -radius)

# Using the design plan's frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means the profile is in the XZ plane (u=X, v=Z), extruded along Y (w)

wp = cq.Workplane("XZ")

# Build the stadium profile
# Start at the top-left corner of the straight section: (radius, radius)
# Go counterclockwise: top line, right arc, bottom line, left arc

# Left arc center: (radius, 0), start angle 90° (top), end angle -90° (bottom) going clockwise
# But we want counterclockwise, so start at -90° (bottom) and go to 90° (top)
# Actually, let's build it as a closed wire using polyline and arcs

# Approach: build the profile as a series of edges
# Start at bottom-left of straight section: (radius, -radius)
# Line to bottom-right: (radius + straight_length, -radius)
# Arc to top-right: center at (radius + straight_length, 0), from -90° to 90°
# Line to top-left: (radius, radius)
# Arc to bottom-left: center at (radius, 0), from 90° to -90° (or 270° to 90° going the other way)

# Using the design plan's curve definitions:
# Arc 1: center (1.0, 0.0) in UV, radius 1.0, start 0°, end 180° -> this is the left arc
# Line 1: from (1.0, -1.0) to (3.8, -1.0) -> bottom line
# Arc 2: center (3.8, 0.0), radius 1.0, start 0°, end 180° -> right arc
# Line 2: from (3.8, 1.0) to (1.0, 1.0) -> top line

# The UV coordinates are in the design plan's local frame, scaled by radius=10 and straight_length=28
# So the actual coordinates are:
# Left arc center: (10, 0), radius 10
# Bottom line: from (10, -10) to (38, -10)
# Right arc center: (38, 0), radius 10
# Top line: from (38, 10) to (10, 10)

# Build the profile using the discretization approach from the original script
N_ARC = 128

# Start at the bottom-left point: (10, -10)
wp = wp.moveTo(10, -10)

# Bottom line to (38, -10)
wp = wp.lineTo(38, -10)

# Right arc: center (38, 0), radius 10, from -90° to 90°
for k in range(1, N_ARC + 1):
    t = -math.pi/2 + (math.pi) * (k / N_ARC)  # from -90° to 90°
    px = 38 + 10 * math.cos(t)
    py = 0 + 10 * math.sin(t)
    wp = wp.lineTo(px, py)

# Top line to (10, 10)
wp = wp.lineTo(10, 10)

# Left arc: center (10, 0), radius 10, from 90° to 270° (or -90° to 90° going the other way)
# Going from 90° to -90° (clockwise) to close the loop
for k in range(1, N_ARC + 1):
    t = math.pi/2 - (math.pi) * (k / N_ARC)  # from 90° down to -90°
    px = 10 + 10 * math.cos(t)
    py = 0 + 10 * math.sin(t)
    wp = wp.lineTo(px, py)

# Close the wire
wp = wp.close()

# Extrude along Y (w_dir = [0,1,0]) by the design plan's distance
result = wp.extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
