import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0002\neg_01\iter_01\generated.step"

# Design parameters from the design plan
# Stadium profile: straight length = 500.0 mm, radius = 50.0 mm
# Extrude distance = 100.0 mm (one side, +w direction)

straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile using cadquery
# The stadium consists of:
# - Left arc (center at (0,0), radius 50, from 180° to 0° going clockwise)
# - Top line from (0, 50) to (500, 50)
# - Right arc (center at (500,0), radius 50, from 0° to 180° going clockwise)
# - Bottom line from (500, -50) to (0, -50)

# We'll build the profile as a wire using the workplane
wp = cq.Workplane("XY")

# Start at the bottom-left corner of the left arc (0, -50)
# Then trace the stadium profile
s = (
    wp.moveTo(0, -radius)
    .threePointArc((radius, -radius), (radius, 0))  # Left arc from bottom to top
    .lineTo(straight_length - radius, radius)  # Top line
    .threePointArc((straight_length, radius), (straight_length, 0))  # Right arc from top to bottom
    .lineTo(radius, -radius)  # Bottom line
    .close()
)

# Extrude the profile
result = s.extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
