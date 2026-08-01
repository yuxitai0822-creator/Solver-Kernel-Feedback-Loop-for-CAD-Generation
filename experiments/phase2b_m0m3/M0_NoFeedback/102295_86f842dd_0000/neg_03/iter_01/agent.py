import cadquery as cq
from cadquery import exporters
import math

# Design Plan: stadium extrusion
# Stadium profile: two arcs (radius=10mm) connected by two lines (straight_length=28mm)
# Extrude 4.0mm in +w direction (which is +Y in world coordinates)
# The profile lies in the XZ plane (u=x, v=z, w=y)

# Build the stadium profile in the XZ plane
# Arc centers at (10, 0) and (38, 0) in UV (XZ) coordinates
# Radius = 10mm, straight length = 28mm (distance between centers = 28mm)

# Use a clean approach: build the profile using two arcs and two lines
# Start at the top-left of the left arc: (20, 0)
# Go along left arc (counterclockwise) to bottom: (0, -10)
# Line to bottom-right: (28, -10)
# Go along right arc (counterclockwise) to top: (48, 0)
# Line back to start: (20, 0)

# Build the wire segment by segment using cadquery's built-in arc and line operations
s = cq.Workplane("XZ")

# Start at top of left arc: (20, 0)
s = s.moveTo(20, 0)

# Left arc: center (10, 0), radius 10, from 0 to 180 degrees (top to bottom)
# Use three-point arc: start (20, 0), mid (10, 10), end (0, 0)
s = s.threePointArc((10, 10), (0, 0))

# Bottom line: from (0, -10) to (28, -10)
s = s.lineTo(28, -10)

# Right arc: center (38, 0), radius 10, from 0 to 180 degrees (bottom to top)
# Use three-point arc: start (28, -10), mid (38, -10), end (48, 0)
s = s.threePointArc((38, -10), (48, 0))

# Top line: from (48, 0) to (20, 0)
s = s.lineTo(20, 0)

# Close the wire
s = s.close()

# Extrude in the +Y direction (which is +w in the design plan)
result = s.extrude(4.0)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102295_86f842dd_0000\neg_03\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)