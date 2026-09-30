import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 11.3 x 21.0 x 3.0 mm
# The perturbation changed the original 1.13 cm to 1.3559999999999999 cm (13.56 mm)
# But the design plan specifies 11.3 mm length_u, so we use that.

# Build the rectangular prism centered at origin on XY plane
result = (
    cq.Workplane("XY")
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0006\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)