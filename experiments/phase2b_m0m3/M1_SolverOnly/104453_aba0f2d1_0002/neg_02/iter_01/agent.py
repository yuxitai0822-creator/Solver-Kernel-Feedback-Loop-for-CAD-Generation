import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_02\iter_01\generated.step"

# Design parameters from the design plan
# The stadium profile has:
#   - straight_length = 50.0 mm (from curves: line from (0,-5) to (50,-5))
#   - radius = 6.25 mm (perturbed from 5.0)
# Extrude distance = 100.0 mm

RADIUS = 6.25
STRAIGHT_LENGTH = 50.0
EXTRUDE_DISTANCE = 100.0

# Build the stadium profile using proper arc construction
# The stadium consists of:
#   - Left semicircle: center (0,0), radius RADIUS, from 90° to -90° (top to bottom)
#   - Bottom line: from (0, -RADIUS) to (STRAIGHT_LENGTH, -RADIUS)
#   - Right semicircle: center (STRAIGHT_LENGTH, 0), radius RADIUS, from -90° to 90° (bottom to top)
#   - Top line: from (STRAIGHT_LENGTH, RADIUS) to (0, RADIUS)

# Using cadquery's Workplane with threePointArc for each semicircle
result = (
    cq.Workplane("XY")
    .moveTo(0, RADIUS)  # Start at top of left semicircle
    .threePointArc(
        (RADIUS, 0),      # Midpoint (rightmost point of left semicircle)
        (0, -RADIUS)      # End at bottom of left semicircle
    )
    .lineTo(STRAIGHT_LENGTH, -RADIUS)  # Bottom straight segment
    .threePointArc(
        (STRAIGHT_LENGTH + RADIUS, 0),  # Midpoint (rightmost point of right semicircle)
        (STRAIGHT_LENGTH, RADIUS)       # End at top of right semicircle
    )
    .lineTo(0, RADIUS)  # Top straight segment back to start
    .close()
    .extrude(EXTRUDE_DISTANCE)
)

exporters.export(result, OUT_STEP_PATH)