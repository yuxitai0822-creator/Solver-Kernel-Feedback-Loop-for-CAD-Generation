import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104283_e5646f96_0000\neg_02\iter_00\generated.step"

# Design Plan parameters:
# - Circle center in UV: (-15.0, 10.0) -> but note the frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
#   This means the sketch plane is YZ (since w_dir = X axis is the extrusion direction)
# - Circle radius: 12.5 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 75.0 mm along +w direction (which is +X)

# Build the part:
# Workplane on YZ (since extrusion is along X)
result = (
    cq.Workplane("YZ")
    .circle(12.5)  # radius 12.5 mm
    .extrude(75.0)  # extrude 75 mm along X (positive direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
