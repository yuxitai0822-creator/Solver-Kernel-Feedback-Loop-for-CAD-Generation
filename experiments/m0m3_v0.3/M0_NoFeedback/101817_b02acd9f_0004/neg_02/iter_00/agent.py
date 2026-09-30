import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0004\neg_02\iter_00/generated.step"

# Design Plan: extruded rectangle
# Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane, then extrude along +w (Y axis)

# Build the rectangle on the XZ plane (since v_dir is -Z, u_dir is X, w_dir is Y)
# The rectangle corners in UV: start_uv=(127.82976131535646, -66.34402294937294)
# But the dimensions are 1200 x 600, so we center at origin for simplicity

# Create workplane on XZ (since w_dir = Y)
wp = cq.Workplane("XZ")

# Rectangle centered at origin, size 1200 x 600
# Note: v_dir is [0,0,-1], so width_v=600 maps to Z direction
# u_dir is [1,0,0], so length_u=1200 maps to X direction
result = wp.rect(1200.0, 600.0, centered=True).extrude(20.0)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
