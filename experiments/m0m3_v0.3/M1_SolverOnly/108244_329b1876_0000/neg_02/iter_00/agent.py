import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_distance=44.45 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle corners in UV space:
#   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
#   This gives width_u = 121.92 mm, height_v = 259.08 mm
#   But the design plan says length_u=1219.2 mm, width_v=2590.8 mm
#   The UV coordinates appear to be in cm (divided by 10), so we multiply by 10
#   to get mm: width_u = 1219.2 mm, height_v = 2590.8 mm

# Build the rectangle in the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
# The sketch plane normal is w_dir = [0,1,0], so we use XY plane and extrude in Y direction

# Rectangle center and dimensions in mm
x_center = (121.17356129030935 + (-0.7464387096940412)) / 2 * 10  # = 602.1356129030765 mm
z_center = (31.299551148092803 + 290.379551148076) / 2 * 10  # = 1608.395511480844 mm
width_x = (121.17356129030935 - (-0.7464387096940412)) * 10  # = 1219.2 mm
width_z = (290.379551148076 - 31.299551148092803) * 10  # = 2590.8 mm

# Extrude distance (w direction = Y axis)
extrude_dist = 44.45  # mm

# Build the part
result = (
    cq.Workplane("XY")
    .center(x_center, z_center)
    .rect(width_x, width_z)
    .extrude(extrude_dist)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108244_329b1876_0000\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)