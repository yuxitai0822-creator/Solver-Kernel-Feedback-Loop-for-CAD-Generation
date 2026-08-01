import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0003\neg_03\iter_00/generated.step"

# Design Plan parameters (converted from cm to mm where needed)
# Outer circle: center_uv = (5.080000162124634, 6.350000202655792) in cm -> (50.80000162124634, 63.50000202655792) in mm
# Radius = 0.4711700000000002 cm -> 4.7117 mm
# Extrude distance = 12.192 mm (already in mm)

# Build the part: a simple disk (extruded circle)
result = (
    cq.Workplane("XY")
    .moveTo(50.80000162124634, 63.50000202655792)
    .circle(4.7117)
    .extrude(12.192)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
