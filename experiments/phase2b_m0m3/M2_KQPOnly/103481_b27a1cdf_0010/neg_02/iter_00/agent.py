import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103481_b27a1cdf_0010\neg_02\iter_00/generated.step"

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The profile is a rectangle centered at origin with half-dimensions 50.8 mm
# Extrude 38.1 mm in +Z direction

# Create the rectangular profile
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6, centered=True)
    .extrude(38.1)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
