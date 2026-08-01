import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0003\neg_01\iter_00/generated.step"

# Design Plan parameters:
# - Disk (extruded circle)
# - Circle center at (16.994661, 17.998557) in sketch plane
# - Circle radius = 25.4 mm
# - Extrude distance = 8.89 mm (one side, +w direction)
# - Body count = 1
# - Span u = 50.8 mm, span v = 50.8 mm, span w = 8.89 mm

# Build the part
result = (
    cq.Workplane("XY")
    .moveTo(16.994661, 17.998557)
    .circle(25.4)
    .extrude(8.89)
)

# Export STEP
exporters.export(result, OUT_STEP_PATH)
