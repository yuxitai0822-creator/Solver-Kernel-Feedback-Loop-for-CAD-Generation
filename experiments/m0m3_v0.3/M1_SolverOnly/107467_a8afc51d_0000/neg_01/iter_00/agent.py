import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Disk with radius 3.0 mm, extrude distance 14.0 mm
# The previous script used 21.0 mm (incorrectly converted from 2.1 cm)
# Correct dimensions from design plan: radius=3.0, extrude=14.0

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107467_a8afc51d_0000\neg_01\iter_00\generated.step"

# Build the disk: circle radius 3.0, extrude 14.0 in +Z direction
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan
    .extrude(14.0)  # extrude distance from design plan
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
