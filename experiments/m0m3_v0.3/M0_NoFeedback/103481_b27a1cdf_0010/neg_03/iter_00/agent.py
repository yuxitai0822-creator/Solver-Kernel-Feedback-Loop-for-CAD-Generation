import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The previous script used perturbed dimensions (81.28 x 81.28 x 38.1) from the perturbation description.
# The design plan specifies 101.6 x 101.6 x 38.1 mm, so we must use those exact values.

# Dimensions from design plan (in mm, already converted from cm)
LENGTH_U = 101.6  # x dimension
WIDTH_V = 101.6   # y dimension
HEIGHT_W = 38.1   # z dimension (extrude distance)

# Build the rectangular prism centered at origin
result = (
    cq.Workplane("XY")
    .rect(LENGTH_U, WIDTH_V)
    .extrude(HEIGHT_W)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103481_b27a1cdf_0010\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)