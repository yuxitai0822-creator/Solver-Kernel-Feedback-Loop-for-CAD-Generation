import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SOIC-8 body
# Dimensions: 3.9 mm (u) x 4.9 mm (v) x 1.55 mm (w)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in uv-plane
# Extrude along +w direction

# Build the rectangle profile (centered at origin)
# u spans from -1.95 to 1.95 (total 3.9 mm)
# v spans from -2.45 to 2.45 (total 4.9 mm)
# Since v_dir = [0,0,-1], we use XZ plane for the sketch

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0000\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)