import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

# Design Plan: rectangular prism 39.0 x 68.0 x 10.0 mm
# The profile is a rectangle with corners at (-3.9, 6.8) and (0.0, 0.0) in UV space
# After unit conversion (cm->mm x10): width = 39.0 mm, height = 68.0 mm
# Extrude distance = 10.0 mm (converted from 1.0 cm)

# Build the rectangle centered at the midpoint of the given corners
x_min = -3.9 * 10  # -39.0
x_max = 0.0 * 10   # 0.0
y_min = 0.0 * 10   # 0.0
y_max = 6.8 * 10   # 68.0

width = x_max - x_min   # 39.0 mm
height = y_max - y_min  # 68.0 mm
center_x = (x_min + x_max) / 2  # -19.5
center_y = (y_min + y_max) / 2  # 34.0

# Create the rectangular prism
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .rect(width, height, centered=True)
    .extrude(10.0)  # 10.0 mm as specified
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
