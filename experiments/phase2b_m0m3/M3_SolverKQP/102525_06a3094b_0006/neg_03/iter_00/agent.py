import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0006\neg_03\iter_00\generated.step"

# Design Plan: rectangular prism, extruded rectangle
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from -0.565 to 0.565, v from -1.05 to 1.05
# After scaling: u range = 11.3 mm, v range = 21.0 mm
# Extrude along +w (y-axis) by 3.0 mm

# Build on XY plane, then rotate to match frame orientation
# Frame: u=x, v=-z, w=y
# So we sketch on XZ plane (u,v) and extrude along Y (w)

# Create the rectangle on XZ plane
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# The rectangle is centered at origin, spanning:
# X: -5.65 to 5.65
# Z: -10.5 to 10.5
# Y: 0 to 3.0
# This matches the design plan dimensions and frame orientation

exporters.export(result, OUT_STEP_PATH)
