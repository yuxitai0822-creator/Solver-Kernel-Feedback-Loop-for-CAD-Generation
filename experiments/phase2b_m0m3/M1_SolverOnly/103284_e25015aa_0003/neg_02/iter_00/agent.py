import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Disk: circle radius 25.4 mm, extrude 8.89 mm
# The perturbed radius from the previous script was 31.75 (incorrect)
# Correct radius from design plan: 25.4 mm

RADIUS = 25.4  # mm
EXTRUDE_DISTANCE = 8.89  # mm

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(RADIUS)
    .extrude(EXTRUDE_DISTANCE)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103284_e25015aa_0003\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)