import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# The design is a disk (extruded circle) with:
# - Circle center in UV: (11.430000364780426, 0.0) but the profile center_uv is (114.300004, 0.0)
#   The profile center_uv is used for positioning in the sketch plane
# - Circle radius: 4.87045 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 6.8707 mm along +w direction
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along y (w=y)

# Parameters from design plan
circle_radius = 4.87045  # mm
circle_center_x = 114.300004  # mm (center_uv[0])
circle_center_y = 0.0  # mm (center_uv[1])
extrude_distance = 6.8707  # mm

# Build the model
# Workplane XZ since u_dir=[1,0,0] (x), v_dir=[0,0,-1] (z), extrude along y
result = (
    cq.Workplane("XZ")
    .moveTo(circle_center_x, circle_center_y)
    .circle(circle_radius)
    .extrude(extrude_distance)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0002\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)