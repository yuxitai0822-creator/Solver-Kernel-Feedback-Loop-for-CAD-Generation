import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The perturbation changes the rectangle half-size from 5.08 to 6.096 (12.192 total width)
# Original design plan: rectangle corners at +/-5.08 -> 10.16 total width
# Perturbation: original=10.16, perturbed=12.192 -> half-size = 6.096
# Using the perturbed value: half-size = 6.096

HALF_SIZE = 6.096  # perturbed half-size (original was 5.08)
EXTENT = 38.1  # extrusion height

# Build the rectangular prism
result = (
    cq.Workplane("XY")
    .rect(2 * HALF_SIZE, 2 * HALF_SIZE)
    .extrude(EXTENT)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103481_b27a1cdf_0010\neg_02\iter_02\generated.step"
exporters.export(result, OUT_STEP_PATH)
