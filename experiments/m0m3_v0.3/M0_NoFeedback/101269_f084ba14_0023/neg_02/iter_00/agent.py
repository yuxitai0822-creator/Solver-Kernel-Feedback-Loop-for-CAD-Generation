import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101269_f084ba14_0023\neg_02\iter_00\generated.step"

# Design Plan parameters (all in mm)
# Rectangle profile in UV frame:
#   U direction: [1.0, 0.0, 0.0] (X axis)
#   V direction: [0.0, 0.0, -1.0] (negative Z axis)
#   W direction: [0.0, 1.0, 0.0] (Y axis)
# Profile rectangle corners in UV coordinates:
#   (0.0, 0.0), (9.525, 0.0), (9.525, 57.15), (0.0, 57.15)
#   Note: The perturbed value 11.43 replaces 9.525 for the U dimension
# Extrude distance: 19.05 mm in +W direction (Y axis)

# Build the rectangle on the XZ plane (since V is -Z, U is X)
# The rectangle spans:
#   U: from 0 to 11.43 (perturbed value)
#   V: from 0 to 57.15
# In world coordinates (X, Z):
#   X: 0 to 11.43
#   Z: -57.15 to 0 (since V direction is -Z, V=0 maps to Z=0, V=57.15 maps to Z=-57.15)

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Build the rectangle centered at (5.715, -28.575) with width 11.43 and height 57.15
# Center in X: (0 + 11.43) / 2 = 5.715
# Center in Z: (0 + (-57.15)) / 2 = -28.575
result = wp.moveTo(5.715, -28.575).rect(11.43, 57.15, centered=True).extrude(19.05)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
