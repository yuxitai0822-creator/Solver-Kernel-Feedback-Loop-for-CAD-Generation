import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Lever Switch - Disk with extruded circle
# Dimensions:
#   Circle radius: 25.4 mm (from profiles[0].radius.value)
#   Extrude distance: 8.89 mm (from extrude.distance_total.value)
#   Center: (16.994661, 17.998557) in UV plane
#
# The previous script had incorrect extrude distance (13.335 mm instead of 8.89 mm)
# and used a complex history-based approach. This script directly implements the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103284_e25015aa_0003\neg_01\iter_00/generated.step"

# Parameters from design plan
radius = 25.4  # mm
extrude_distance = 8.89  # mm (corrected from 13.335)
center_x = 16.994661
center_y = 17.998557

# Build the disk
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
