import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm
# Perturbation: extrude depth changed from 38.1 to 57.15 mm (5.715 cm * 10)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103481_b27a1cdf_0010\neg_01\iter_00/generated.step"

# Build the rectangular prism centered at origin
# Profile: 101.6 x 101.6 mm square (from design plan dimensions)
# Extrude: 57.15 mm (perturbed value: 5.715 cm * 10 = 57.15 mm)

result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(57.15)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
