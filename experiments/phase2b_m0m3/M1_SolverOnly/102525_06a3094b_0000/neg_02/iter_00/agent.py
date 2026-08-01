import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0000\neg_02\iter_00\generated.step"

# Build the rectangular prism according to the design plan.
# The profile is a rectangle centered at (0,0) in the XY plane.
# Dimensions: length_u = 3.9 mm (along X), width_v = 4.9 mm (along Y).
# Extrude distance = 1.55 mm along +Z.

result = (
    cq.Workplane("XY")
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

exporters.export(result, OUT_STEP_PATH)
