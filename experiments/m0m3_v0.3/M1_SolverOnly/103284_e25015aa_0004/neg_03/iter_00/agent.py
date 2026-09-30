import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103284_e25015aa_0004\neg_03\iter_00\generated.step"

# Design Plan: single disk, radius=11.938 mm, extrude=12.7 mm, no inner holes
radius = 11.938
height = 12.7

# Build the disk centered at origin (the design plan's center_uv is just a sketch offset, we center for simplicity)
result = cq.Workplane("XY").circle(radius).extrude(height)

# Export
exporters.export(result, OUT_STEP_PATH)
