import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 5.5372  # mm (original: 0.55372 cm * 10)
INNER_RADIUS = 1.9812  # mm (original: 0.19812 cm * 10)
CENTER_X = -25.40000081062317  # mm (original: -2.540000081062317 cm * 10)
CENTER_Y = 12.700000405311584  # mm (original: 1.2700000405311584 cm * 10)
EXTRUDE_DISTANCE = 1.3208  # mm (original: 0.13208 cm * 10)

# Output path
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0004\neg_02\iter_00/generated.step"

# Build the washer using cadquery
# Create a workplane on the XY plane (default)
result = (
    cq.Workplane("XY")
    .moveTo(CENTER_X, CENTER_Y)
    .circle(OUTER_RADIUS)
    .extrude(EXTRUDE_DISTANCE)
    .faces(">Z")  # Select the top face
    .workplane()
    .hole(INNER_RADIUS * 2, EXTRUDE_DISTANCE)  # Through hole
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
