import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_02\iter_00/generated.step"

# Design parameters from the design plan
# The stadium profile has:
#   - straight_length = 500.0 mm (inferred from point span, but the curves show 50.0 mm straight? Let's check)
#   - radius = 50.0 mm (from curve_field, but the perturbed radius is 6.25? Wait, the perturbation says radius changed from 5.0 to 6.25)
# Actually looking at the curves:
#   Arc1: center (0,0), radius 5.0, start 0, end 180
#   Line1: (0, -5) to (50, -5)
#   Arc2: center (50,0), radius 5.0, start 0, end 180
#   Line2: (50, 5) to (0, 5)
# So the straight length is 50.0 mm, radius is 5.0 mm
# But the perturbation says radius changed from 5.0 to 6.25
# Let's use the perturbed values: radius = 6.25, straight_length = 50.0
# Extrude distance = 100.0 mm

RADIUS = 6.25  # perturbed from 5.0
STRAIGHT_LENGTH = 50.0
EXTRUDE_DISTANCE = 100.0

# Build the stadium profile
# Start with the first arc at (0,0) going from 0 to 180 degrees (top half)
# Then line from (0, -RADIUS) to (STRAIGHT_LENGTH, -RADIUS)
# Then arc at (STRAIGHT_LENGTH, 0) from 0 to 180 degrees (bottom half)
# Then line from (STRAIGHT_LENGTH, RADIUS) back to (0, RADIUS)

# Using cadquery's Workplane to build the profile
result = (
    cq.Workplane("XY")
    .moveTo(0, RADIUS)  # Start at top-left of the first arc
    .threePointArc(
        (RADIUS, 0),  # Midpoint of the arc (top of the circle)
        (0, -RADIUS)  # End of the arc
    )
    .lineTo(STRAIGHT_LENGTH, -RADIUS)  # Bottom line
    .threePointArc(
        (STRAIGHT_LENGTH + RADIUS, 0),  # Midpoint of the second arc
        (STRAIGHT_LENGTH, RADIUS)  # End of the second arc
    )
    .lineTo(0, RADIUS)  # Top line back to start
    .close()
    .extrude(EXTRUDE_DISTANCE)
)

exporters.export(result, OUT_STEP_PATH)
