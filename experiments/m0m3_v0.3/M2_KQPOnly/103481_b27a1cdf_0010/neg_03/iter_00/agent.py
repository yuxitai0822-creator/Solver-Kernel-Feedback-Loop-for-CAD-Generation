import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The previous script used perturbed dimensions (81.28 x 81.28 x 38.1)
# This script reconstructs the correct geometry from the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103481_b27a1cdf_0010\neg_03\iter_00/generated.step"

# Dimensions from design plan (in mm)
length_u = 101.6  # along X
width_v = 101.6   # along Y
extrude_distance = 38.1  # along Z

# Build the rectangular prism
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
importers = None
exporters.export(result, OUT_STEP_PATH)
