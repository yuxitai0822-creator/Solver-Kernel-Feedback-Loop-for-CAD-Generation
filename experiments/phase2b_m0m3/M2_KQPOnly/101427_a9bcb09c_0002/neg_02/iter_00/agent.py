import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u = 1930.0 mm, width_v = 550.0 mm, extrude_distance = 50.0 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means the rectangle lies in the XZ plane (u=X, v=Z), extruded along Y (w=Y)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0002\neg_02\iter_00/generated.step"

# Build the rectangle in the XZ plane (workplane 'XZ')
# The rectangle spans from (0,0) to (1930, 550) in the XZ plane
# Using centered=False to match the exact corner coordinates
wp = cq.Workplane("XZ")

# Create the rectangle at the origin, then extrude along Y (positive direction)
# The rectangle corners: (0,0), (1930,0), (1930,550), (0,550)
# Using rect with centered=False places the rectangle with lower-left corner at the current point
result = wp.rect(1930.0, 550.0, centered=False).extrude(50.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
