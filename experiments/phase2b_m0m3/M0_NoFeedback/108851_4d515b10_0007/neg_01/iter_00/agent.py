import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4mm x 50.8mm x 19.05mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile in uv-plane: rectangle from (0,0) to (27.94, 5.08) in cm -> (279.4, 50.8) in mm
# Extrude along +w direction by 19.05mm

# Build the rectangle profile on the XZ plane (since v_dir is [0,0,-1], u_dir is [1,0,0])
# The profile coordinates are in uv-space: u from 0 to 279.4, v from 0 to 50.8
# We'll create the rectangle centered at (139.7, 25.4) on the XZ plane

result = (
    cq.Workplane("XZ")
    .center(139.7, -25.4)  # center the rectangle; v_dir is [0,0,-1] so we negate v
    .rect(279.4, 50.8)
    .extrude(19.05)  # extrude along +w = [0,1,0] which is Y direction
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0007\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)