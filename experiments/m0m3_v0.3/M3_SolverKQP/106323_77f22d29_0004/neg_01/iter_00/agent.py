import cadquery as cq
from cadquery import exporters
import math

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# Perturbation: OneSide extent (extrude in +Z direction only, not symmetric)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106323_77f22d29_0004\neg_01\iter_00/generated.step"

# Build the annulus profile on XY plane
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer circle
    .circle(12.5)  # inner circle (creates a hole)
    .extrude(10.0)  # extrude in +Z direction only (OneSide)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
