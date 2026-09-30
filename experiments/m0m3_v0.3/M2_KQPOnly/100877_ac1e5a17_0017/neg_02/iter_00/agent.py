import cadquery as cq
from cadquery import exporters
import math

# Design Plan: flat rectangular plate 254.0 x 190.5 x 3.175 mm
# The previous script had incorrect coordinates (shifted by -25.4 in x and had 279.4 width instead of 254.0)
# This script builds the correct rectangle centered at origin with proper dimensions

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0017\neg_02\iter_00/generated.step"

# Dimensions from design plan (in mm)
length_u = 254.0  # along x-axis
width_v = 190.5   # along y-axis
thickness = 3.175 # along z-axis

# Build the plate centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(thickness)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
