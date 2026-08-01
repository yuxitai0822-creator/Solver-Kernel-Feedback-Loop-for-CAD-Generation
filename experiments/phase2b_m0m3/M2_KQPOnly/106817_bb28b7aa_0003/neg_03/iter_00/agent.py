import cadquery as cq
from cadquery import exporters
import math

# Design Plan: ruler holder w/screw - disk with single extruded circle
# Dimensions from design plan:
#   Circle center: (5.080000162124634, 6.350000202655792) in UV frame
#   Circle radius: 0.4711700000000002 (but note: dimensions section says radius=4.7117)
#   Extrude distance: 12.192 mm
# The design plan shows a single outer circle with no inner loops.
# The previous script incorrectly added an inner loop (radius 0.5) which is not in the design plan.
# Also, the center coordinates in the design plan's profiles section are (50.800002, 63.500002)
# which is 10x the curves center - this is due to cm->mm conversion.
# The curves center (5.08, 6.35) is in cm, so multiply by 10 for mm: (50.8, 63.5)
# Radius: curves says 0.47117 cm = 4.7117 mm, dimensions says 4.7117 mm - consistent.

# Build the part according to design plan:
# - Single outer circle at (50.8, 63.5) with radius 4.7117 mm
# - Extrude 12.192 mm in +w direction (which is +Y in our frame)
# - No inner holes

# Create workplane on XZ plane (as in original), but extrude along Y
wp = cq.Workplane("XZ")

# Create the outer circle
center_x = 50.800002
center_y = 63.500002
radius = 4.7117

# Build the circle and extrude
result = wp.moveTo(center_x, center_y).circle(radius).extrude(12.192)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0003\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
