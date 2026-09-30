import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_03\iter_01/generated.step"

# Design parameters from the design plan:
# Stadium profile: straight_length = 500.0 mm, radius = 50.0 mm
# Extrude distance = 100.0 mm
# The profile is defined in the XY plane (u=x, v=y, w=z)

straight_length = 500.0  # mm
radius = 50.0  # mm
extrude_distance = 100.0  # mm

# Build the stadium profile using a clean, direct approach:
# 1. Create a rectangle of size straight_length x (2*radius)
# 2. Add fillets at the two ends to create the stadium shape
# This is more robust than manual arc construction

result = (
    cq.Workplane("XY")
    .rect(straight_length, 2 * radius)
    .extrude(extrude_distance)
    .faces(">X").fillet(radius)  # Fillet the right end
    .faces("<X").fillet(radius)  # Fillet the left end
)

# Export the result
exporters.export(result, OUT_STEP_PATH)
