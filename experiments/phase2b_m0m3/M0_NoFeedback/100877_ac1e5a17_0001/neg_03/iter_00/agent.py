import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm
# The perturbation changes the y-dimension from 215.9 to 17.272 (incorrectly small)
# We must follow the design plan exactly: 215.9 mm in y (v direction)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100877_ac1e5a17_0001\neg_03\iter_00\generated.step"

# Build the rectangular plate according to design plan
# Profile: rectangle 279.4 mm (u/x) x 215.9 mm (v/y)
# Extrude: 1.5875 mm in +w/z direction

result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9, centered=False)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
