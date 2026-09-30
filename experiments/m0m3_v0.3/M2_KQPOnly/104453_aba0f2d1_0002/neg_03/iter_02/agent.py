import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_03\iter_02/generated.step"

# Design parameters from the design plan:
# Stadium profile: straight_length = 500.0 mm, radius = 50.0 mm
# Extrude distance = 100.0 mm
# The stadium is centered along the x-axis (u direction) from 0 to 500, with arcs at ends.
# The profile lies in the XY plane, extruded in +Z direction.

straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile using cadquery's built-in arc and line construction.
# The stadium consists of:
# - Left arc: center at (0, 0), radius 50, from 90° to -90° (or 0 to 180 in the design plan's local UV)
# - Bottom line: from (0, -50) to (500, -50)
# - Right arc: center at (500, 0), radius 50, from -90° to 90° (or 0 to 180)
# - Top line: from (500, 50) to (0, 50)
#
# We use threePointArc for exact arcs.

# Create a workplane on XY
wp = cq.Workplane("XY")

# Build the stadium wire using threePointArc and lineTo.
# Start at the left arc top point: (0, 50)
# Arc from (0, 50) to (0, -50) with center (0, 0) -> this is a 180° arc
# Line from (0, -50) to (500, -50)
# Arc from (500, -50) to (500, 50) with center (500, 0) -> 180° arc
# Line from (500, 50) back to (0, 50)

# Use threePointArc: start point, middle point, end point.
# For left arc: start (0, 50), middle (0, 0) (center), end (0, -50) -> but threePointArc expects three points on the arc, not center.
# Actually, threePointArc takes three points on the arc: start, a point on the arc, end.
# For a 180° arc from (0,50) to (0,-50) with center (0,0), the midpoint on the arc is (-50, 0).
# So left arc: start (0,50), mid (-50,0), end (0,-50).
# Right arc: start (500,-50), mid (550,0), end (500,50).

# Build the profile as a closed wire.
# Start at (0, 50)
wire = (wp.moveTo(0, 50)
        .threePointArc((-50, 0), (0, -50))  # left arc
        .lineTo(500, -50)                    # bottom line
        .threePointArc((550, 0), (500, 50))  # right arc
        .lineTo(0, 50)                       # top line
        .close()
        .extrude(extrude_distance))

result = wire

exporters.export(result, OUT_STEP_PATH)
