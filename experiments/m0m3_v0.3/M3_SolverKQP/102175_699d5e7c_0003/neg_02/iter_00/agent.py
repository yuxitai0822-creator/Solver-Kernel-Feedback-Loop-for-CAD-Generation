import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102175_699d5e7c_0003\neg_02\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 39.0 x 68.0 x 10.0 mm
# The profile is a rectangle with corners at uv coordinates:
#   (-3.9, 6.8), (0.0, 6.8), (-3.9, 0.0), (0.0, 0.0)
# This defines a rectangle of width 3.9 mm and height 6.8 mm in uv space.
# However, the design plan states length_u = 39.0 mm and width_v = 68.0 mm.
# The uv coordinates appear to be scaled by 10x (cm to mm conversion factor).
# So the actual rectangle in mm is: width = 39.0 mm, height = 68.0 mm.
# The uv coordinates given are: start_uv = (-3.9, 6.8), end_uv = (0.0, 6.8), etc.
# This means the rectangle spans from x=-3.9 to x=0.0 (width 3.9) and y=0.0 to y=6.8 (height 6.8).
# After cm->mm conversion (x10): width = 39.0 mm, height = 68.0 mm.
# The extrude distance is 10.0 mm.

# Build the rectangle centered at the midpoint of the uv coordinates
x_min = -3.9 * 10  # -39.0 mm
x_max = 0.0 * 10   # 0.0 mm
y_min = 0.0 * 10   # 0.0 mm
y_max = 6.8 * 10   # 68.0 mm

width = x_max - x_min  # 39.0 mm
height = y_max - y_min  # 68.0 mm
center_x = (x_min + x_max) / 2  # -19.5 mm
center_y = (y_min + y_max) / 2  # 34.0 mm

# Create the rectangular prism
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .rect(width, height, centered=True)
    .extrude(10.0)  # extrude distance in mm
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
