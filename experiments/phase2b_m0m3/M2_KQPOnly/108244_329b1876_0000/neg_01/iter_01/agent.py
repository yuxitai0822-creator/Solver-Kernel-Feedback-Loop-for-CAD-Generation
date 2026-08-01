import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle corners in uv:
#   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
#
# The uv coordinates are in mm, but the expected spans are:
#   u span = 121.17356129030935 - (-0.7464387096940412) = 121.92 mm  (expected 1219.2 mm)
#   v span = 290.379551148076 - 31.299551148092803 = 259.08 mm  (expected 2590.8 mm)
# This indicates the uv coordinates are in cm, not mm. The design plan says unit_conversion_applied: cm_to_mm (x10).
# So we must multiply the uv coordinates by 10 to get mm.

# Convert uv coordinates from cm to mm (multiply by 10)
scale = 10.0

x_min = -0.7464387096940412 * scale
x_max = 121.17356129030935 * scale
z_min = 31.299551148092803 * scale
z_max = 290.379551148076 * scale

width_x = x_max - x_min  # 1219.2 mm
length_z = z_max - z_min  # 2590.8 mm
center_x = (x_min + x_max) / 2
center_z = (z_min + z_max) / 2

# Extrude distance (along w_dir = [0,1,0]) - already in mm
extrude_dist = 44.45  # mm

# Build the part on the XZ plane, extrude along Y
result = (cq.Workplane("XZ")
    .moveTo(center_x, center_z)
    .rect(width_x, length_z, centered=True)
    .extrude(extrude_dist)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108244_329b1876_0000\neg_01\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)