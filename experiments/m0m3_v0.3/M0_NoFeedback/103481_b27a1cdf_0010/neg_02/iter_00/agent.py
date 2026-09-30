import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The previous script used perturbed coordinates (60.96, -50.8) which gave 121.92 x 101.6
# We need to match the design plan dimensions exactly.

# From design plan:
# rectangle centered at origin, half-width = 5.08 cm = 50.8 mm (since 101.6/2 = 50.8)
# But the UV coordinates in the plan show start_uv = [5.08, -5.08] etc, which are in cm
# After cm->mm conversion: 5.08 cm = 50.8 mm

# The rectangle should be centered at origin with width=101.6, height=101.6
# Extrude 38.1 mm in +Z direction

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103481_b27a1cdf_0010\neg_02\iter_00\generated.step"

# Build the rectangular prism
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)  # width=101.6, height=101.6, centered at origin
    .extrude(38.1)        # extrude 38.1 mm in +Z
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
