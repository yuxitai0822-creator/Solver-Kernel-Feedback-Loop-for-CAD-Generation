import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
RADIUS = 0.8  # mm (from dimensions.radius)
HEIGHT = 4.0  # mm (from extrude.distance_total.value)

# Build the disk: a simple cylinder
# Using XY plane as sketch plane, extrude along Z
result = (
    cq.Workplane("XY")
    .circle(RADIUS)
    .extrude(HEIGHT)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102760_26430589_0037\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
