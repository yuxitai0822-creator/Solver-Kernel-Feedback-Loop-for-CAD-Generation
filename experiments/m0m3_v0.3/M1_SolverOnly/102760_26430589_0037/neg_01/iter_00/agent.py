import cadquery as cq
from cadquery import exporters
import math

# Design Plan: disk with radius 0.8 mm, extrude 4.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Circle center at (0,0) in UV plane, radius 0.8
# Extrude along -w direction (negative Y in world) by 4.0 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102760_26430589_0037\neg_01\iter_00/generated.step"

# Build the disk
# Workplane is XZ (since v_dir is [0,0,-1], w_dir is [0,1,0])
# Circle in XZ plane, extrude along Y (negative Y for -w direction)
result = (
    cq.Workplane("XZ")
    .circle(0.8)  # radius from design plan
    .extrude(4.0)  # extrude distance from design plan
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
