import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 8.5 x 18.0 x 2.5 mm
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Profile rectangle centered at origin in uv-plane
# Extrude +w direction by 2.5 mm

# Build the rectangle profile on XZ plane (since v is [0,0,-1] and w is [0,1,0],
# the uv-plane corresponds to XZ plane in cadquery)
# Rectangle dimensions: length_u=8.5 (along X), width_v=18.0 (along Z)
# Center at origin

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)  # extrude along +Y (which is +w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0004\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)