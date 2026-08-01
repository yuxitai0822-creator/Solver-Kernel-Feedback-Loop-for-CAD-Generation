import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102175_699d5e7c_0003\neg_02\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 39.0 x 68.0 x 10.0 mm
# The profile is a rectangle with corners at uv coordinates:
#   (-3.9, 0.0) -> (0.0, 0.0) -> (0.0, 6.8) -> (-3.9, 6.8)
# This gives width = 3.9 mm along u, height = 6.8 mm along v.
# However, the dimensions table says length_u = 39.0 mm, width_v = 68.0 mm.
# The uv coordinates appear to be in cm (since compiler notes say cm_to_mm x10).
# So we scale by 10: width = 3.9 * 10 = 39.0 mm, height = 6.8 * 10 = 68.0 mm.
# Extrude distance = 10.0 mm (already in mm).

# Build the rectangle centered at origin for simplicity
width = 39.0  # mm (3.9 cm * 10)
height = 68.0  # mm (6.8 cm * 10)
extrude_depth = 10.0  # mm

result = (
    cq.Workplane("XY")
    .rect(width, height, centered=True)
    .extrude(extrude_depth)
)

exporters.export(result, OUT_STEP_PATH)
