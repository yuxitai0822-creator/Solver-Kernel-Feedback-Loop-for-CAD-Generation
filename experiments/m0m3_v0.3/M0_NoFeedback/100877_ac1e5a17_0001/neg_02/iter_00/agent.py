import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# The perturbation changes the original 27.94 to 33.528 (affecting the rectangle width)
# Original rectangle: 27.94 x 21.59 -> Perturbed: 33.528 x 21.59 (scaled by 1.2)
# But the design plan specifies length_u=279.4, width_v=215.9, so we use those values

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100877_ac1e5a17_0001\neg_02\iter_00\generated.step"

# Build the rectangular plate
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
