import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism, 39.0 x 68.0 x 10.0 mm
# The perturbed width_v is 5.44 (from 6.8), but the design plan says 68.0 mm total.
# The original script had incorrect coordinates (negative values, wrong scaling).
# We build a simple rectangle centered at origin, then extrude.

# Dimensions from design plan (in mm, after cm->mm conversion)
length_u = 39.0  # along X
width_v = 68.0   # along Y
extrude_w = 10.0 # along Z

# Build the rectangular prism
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_w)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102175_699d5e7c_0003\neg_03\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
