import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0002\neg_03\iter_00/generated.step"

# Design parameters from the design plan
# Stadium profile: straight length = 500.0 mm, radius = 50.0 mm
# But note: the design plan says straight_length = 500.0, radius = 50.0
# However the curves in the profile show:
#   arc at (0,0) radius 5.0, start 0, end 180
#   line from (0,-5) to (50,-5)
#   arc at (50,0) radius 5.0, start 0, end 180
#   line from (50,5) to (0,5)
# This is a small stadium with straight_length=50, radius=5
# The dimensions section says straight_length=500.0, radius=50.0 (10x larger)
# This is because unit conversion cm->mm was applied (x10)
# So the actual geometry is: straight_length=50mm, radius=5mm
# Extrude distance = 100.0 mm

straight_length = 50.0  # mm
radius = 5.0  # mm
extrude_distance = 100.0  # mm

# Build the stadium profile
# Start with the workplane
result = (
    cq.Workplane("XY")
    .moveTo(0, 0)
    .lineTo(straight_length, 0)
    .threePointArc(
        (straight_length + radius, radius),
        (straight_length, 2 * radius)
    )
    .lineTo(0, 2 * radius)
    .threePointArc(
        (-radius, radius),
        (0, 0)
    )
    .close()
    .extrude(extrude_distance)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
