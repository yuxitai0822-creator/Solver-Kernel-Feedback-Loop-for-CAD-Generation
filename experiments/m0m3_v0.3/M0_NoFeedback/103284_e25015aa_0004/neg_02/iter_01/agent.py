import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0004\neg_02\iter_01/generated.step"

# Design Plan parameters:
# - Extruded circle (disk)
# - Radius = 11.938 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance = 12.7 mm
# - Center at (8.077681, 8.284339) in the sketch plane

radius = 11.938  # mm
height = 12.7    # mm
center_x = 8.077681
center_y = 8.284339

# Build the disk: create a circle at the specified center, extrude it
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(height)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)