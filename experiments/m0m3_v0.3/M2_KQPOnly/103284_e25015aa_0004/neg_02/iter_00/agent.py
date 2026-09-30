import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
RADIUS = 11.938  # mm (original 1.1938 cm * 10 = 11.938 mm)
EXTENT_TOTAL_MM = 12.7  # mm
CENTER_X = 8.077681  # mm (0.8077681283573162 cm * 10)
CENTER_Y = 8.284339  # mm (0.8284338720164226 cm * 10)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0004\neg_02\iter_00/generated.step"

# Build the part: a simple extruded circle (disk)
result = (
    cq.Workplane("XY")
    .moveTo(CENTER_X, CENTER_Y)
    .circle(RADIUS)
    .extrude(EXTENT_TOTAL_MM)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
