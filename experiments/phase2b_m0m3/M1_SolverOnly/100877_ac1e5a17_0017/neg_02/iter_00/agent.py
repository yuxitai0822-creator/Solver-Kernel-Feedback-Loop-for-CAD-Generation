import cadquery as cq
from cadquery import exporters
import math

# Design Plan: flat rectangular plate 254.0 x 190.5 x 3.175 mm
# The perturbation description says original=25.4, perturbed=30.48 (cm->mm conversion)
# But the design plan explicitly states length_u=254.0, width_v=190.5, extrude=3.175
# We follow the design plan dimensions exactly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0017\neg_02\iter_00/generated.step"

# Create the rectangular plate centered at origin
# Dimensions from design plan: length_u=254.0, width_v=190.5, extrude=3.175
length = 254.0  # mm (along X)
width = 190.5   # mm (along Y)
thickness = 3.175  # mm (along Z)

# Build the plate
result = (
    cq.Workplane("XY")
    .rect(length, width, centered=True)
    .extrude(thickness)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
