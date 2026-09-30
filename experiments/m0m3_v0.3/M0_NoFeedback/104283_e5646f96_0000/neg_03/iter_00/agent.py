import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0000\neg_03\iter_00/generated.step"

# Design Plan: extruded circle (disk)
# - Circle center in UV: (-15.0, 10.0) but in the design plan the profile center_uv is [-1.5, 1.0] (scaled?)
#   Actually the dimensions section says center_uv: [-15.0, 10.0] and radius: 12.5
# - Extrude distance: 75.0 mm along +w direction
# - Frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
#   This means the sketch plane is YZ (u,v) and extrude along X (w)
# - The part is a simple cylinder (disk) with no inner holes

# Build the cylinder on YZ plane, extrude along X
result = (
    cq.Workplane("YZ")
    .moveTo(-15.0, 10.0)  # center in YZ plane
    .circle(12.5)          # radius
    .extrude(75.0)         # extrude along X (positive direction)
)

exporters.export(result, OUT_STEP_PATH)
