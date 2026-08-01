import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0004\neg_03\iter_00\generated.step"

# Design Plan parameters:
# - Circle center in UV: (8.077681, 8.284339)
# - Circle radius: 11.938 mm (from dimensions.radius.value)
# - Extrude distance: 12.7 mm in +w direction

# Build the part:
# 1. Create a workplane on XY plane
# 2. Draw a circle at the specified center with the specified radius
# 3. Extrude by 12.7 mm in the +Z direction

result = (
    cq.Workplane("XY")
    .moveTo(8.077681, 8.284339)
    .circle(11.938)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
