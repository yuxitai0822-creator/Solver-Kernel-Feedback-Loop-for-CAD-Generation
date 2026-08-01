import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 39.0 x 68.0 x 10.0 mm
# The previous script used 15.0 mm (perturbed) but the design plan says 10.0 mm
# Also the rectangle coordinates were scaled incorrectly (multiplied by 10)
# The design plan shows rectangle from (-3.9, 0) to (0, 6.8) in UV space
# After unit conversion (cm->mm x10): from (-39, 0) to (0, 68)
# Extrude distance: 10.0 mm (from design plan, not the perturbed 15.0)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

# Build the rectangle profile
# UV coordinates from design plan: start_uv and end_uv for each curve
# The rectangle corners are at (-3.9, 0) and (0, 6.8) in UV space
# After cm->mm conversion (x10): (-39, 0) and (0, 68)

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Build the rectangle: center at (-19.5, 34), width=39, height=68
# Using the corners from the design plan curves:
# Curve 0: (-3.9, 6.8) -> (0, 6.8)  [top edge]
# Curve 1: (-3.9, 0) -> (-3.9, 6.8) [left edge]
# Curve 2: (0, 0) -> (-3.9, 0)      [bottom edge]
# Curve 3: (0, 6.8) -> (0, 0)       [right edge]
# After cm->mm: multiply by 10
x_min = -39.0
x_max = 0.0
y_min = 0.0
y_max = 68.0

width = x_max - x_min  # 39.0
height = y_max - y_min  # 68.0
center_x = (x_min + x_max) / 2  # -19.5
center_y = (y_min + y_max) / 2  # 34.0

# Create the rectangle and extrude
result = (
    wp
    .moveTo(center_x, center_y)
    .rect(width, height, centered=True)
    .extrude(10.0)  # Extrude distance from design plan: 10.0 mm
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
