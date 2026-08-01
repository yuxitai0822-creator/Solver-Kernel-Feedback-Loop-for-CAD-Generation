import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 3.49  # mm
INNER_RADIUS = 2.0   # mm
EXTRUDE_HEIGHT = 0.36  # mm (corrected from perturbed value 0.54)

# Build the washer
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(EXTRUDE_HEIGHT)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107055_0500fdd1_0027\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
