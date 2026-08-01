import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle corners in uv: 
#   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
# Note: The design plan specifies extrude_distance=44.45 mm (not the perturbed 66.675 mm)

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
# The uv coordinates map to xz coordinates

# Compute rectangle parameters
x_min = -0.7464387096940412
x_max = 121.17356129030935
z_min = 31.299551148092803
z_max = 290.379551148076

width_x = x_max - x_min  # 121.92 mm
length_z = z_max - z_min  # 259.08 mm
center_x = (x_min + x_max) / 2
center_z = (z_min + z_max) / 2

# Extrude distance (along w_dir = [0,1,0])
extrude_dist = 44.45  # mm

# Build the part
result = (cq.Workplane("XZ")
    .moveTo(center_x, center_z)
    .rect(width_x, length_z, centered=True)
    .extrude(extrude_dist)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108244_329b1876_0000\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)