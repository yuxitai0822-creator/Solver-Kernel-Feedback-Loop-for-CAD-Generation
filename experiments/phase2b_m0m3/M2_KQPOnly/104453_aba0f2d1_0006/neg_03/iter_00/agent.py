import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular frame (hollow box) with outer 500x300 mm, inner 400x200 mm, extruded 500 mm
# Perturbation: void removed -> make solid block (no inner hole)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0006\neg_03\iter_00\generated.step"

# Build the outer rectangle (500 x 300 mm) on XY plane, centered at origin
result = (
    cq.Workplane("XY")
    .center(250, 150)  # center of rectangle
    .rect(500, 300)
    .extrude(500)  # extrude 500 mm in +Z direction
)

# Perturbation: void removed -> do NOT cut inner hole, keep as solid block
# (No inner loop subtraction)

exporters.export(result, OUT_STEP_PATH)
