import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0000\neg_01\iter_00\generated.step"

# Design Plan parameters (converted from cm to mm where needed)
# Profile: circle at center_uv = (-15.0, 10.0) with radius 12.5 mm
# Extrude: one_side in +w direction, distance 75.0 mm
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# This means the sketch plane is YZ (since w is X axis, sketch is in YZ)

# Build the circle on YZ plane
result = (
    cq.Workplane("YZ")
    .center(-15.0, 10.0)
    .circle(12.5)
    .extrude(75.0)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
