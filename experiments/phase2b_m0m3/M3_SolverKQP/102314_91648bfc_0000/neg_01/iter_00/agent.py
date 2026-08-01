import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
OUTER_RADIUS = 12.7  # mm
INNER_RADIUS = 7.965948  # mm
EXTRUDE_DISTANCE = 101.6  # mm (original 10.16 cm = 101.6 mm, not the perturbed 15.24 cm)

# Build the part
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(EXTRUDE_DISTANCE)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102314_91648bfc_0000\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
