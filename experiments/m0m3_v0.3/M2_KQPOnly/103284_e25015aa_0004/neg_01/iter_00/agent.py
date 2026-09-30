import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Tail Stock Lever - extruded circle
# Dimensions:
#   radius = 11.938 mm (from design plan: radius value 11.938, tol 0.01)
#   extrude distance = 12.7 mm (from design plan: distance_total value 12.7, tol 0.01)
#   center_uv = (8.077681, 8.284339) - used for positioning in sketch plane
#
# Perturbation: E2_extrude_depth - original=1.27cm=12.7mm, perturbed=1.905cm=19.05mm
# The previous script used 19.05mm which is the perturbed value.
# However, the design plan specifies 12.7mm as the target.
# Since this is iteration 0 and we need to match the design plan,
# we use the design plan value of 12.7mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0004\neg_01\iter_00/generated.step"

# Parameters from design plan
radius = 11.938  # mm
center_x = 8.077681  # mm
center_y = 8.284339  # mm
extrude_distance = 12.7  # mm

# Build the part
# Start with a new workplane on XY plane
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
