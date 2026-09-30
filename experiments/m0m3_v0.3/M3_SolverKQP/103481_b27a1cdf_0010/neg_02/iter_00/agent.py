import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# The previous script used perturbed coordinates from a JSON file.
# This script directly implements the design plan dimensions.

# Create a rectangular prism centered at origin
# Width = 101.6 mm (along X), Depth = 101.6 mm (along Y), Height = 38.1 mm (along Z)
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103481_b27a1cdf_0010\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)