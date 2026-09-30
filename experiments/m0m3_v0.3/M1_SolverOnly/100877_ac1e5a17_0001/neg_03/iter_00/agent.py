import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm
# The perturbation changes the y-dimension from 215.9 to 172.72 (21.59 -> 17.272 in cm, then *10 for mm)
# But the design plan shows original 215.9, so we use the perturbed value: 172.72 mm

# Build the rectangular plate
result = (
    cq.Workplane("XY")
    .rect(279.4, 172.72)  # width (x), height (y) - perturbed y dimension
    .extrude(1.5875)       # thickness in z
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0001\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)