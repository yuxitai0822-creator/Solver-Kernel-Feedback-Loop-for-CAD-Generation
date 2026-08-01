import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 17.5  # mm (converted from 1.75 cm)
INNER_RADIUS = 12.5  # mm (converted from 1.25 cm)
TOTAL_HEIGHT = 10.0  # mm (converted from 1.0 cm)

# Build the part
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(TOTAL_HEIGHT / 2, both=True)  # symmetric extrusion
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106323_77f22d29_0004\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)