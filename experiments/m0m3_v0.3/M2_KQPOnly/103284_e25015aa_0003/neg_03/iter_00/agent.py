import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0003\neg_03\iter_00\generated.step"

# Design Plan parameters:
# - Circle center at (16.994660913961006, 17.998556732836484) in XY plane
# - Radius = 25.4 mm (outer circle)
# - Extrude distance = 8.89 mm in +Z direction
# - No inner holes (the previous script had an erroneous inner loop with radius 0.5)
# - Expected body count: 1
# - Expected spans: u=50.8, v=50.8, w=8.89

# Build the part:
result = (
    cq.Workplane("XY")
    .moveTo(16.994660913961006, 17.998556732836484)
    .circle(25.4)
    .extrude(8.89)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
