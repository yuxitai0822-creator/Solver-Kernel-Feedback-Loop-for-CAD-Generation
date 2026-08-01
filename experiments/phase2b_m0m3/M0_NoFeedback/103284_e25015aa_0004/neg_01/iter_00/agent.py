import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Tail Stock Lever - extruded circle
# Dimensions:
#   radius = 11.938 mm (from profile radius)
#   extrude distance = 12.7 mm (from explicit dimension)
#   center_uv = (8.077681, 8.284339) - used for positioning
#
# The previous script had incorrect extrude distance (19.05 mm instead of 12.7 mm)
# and unnecessarily complex logic for reading from JSON history.
# This script directly implements the design plan specifications.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0004\neg_01\iter_00/generated.step"

# Parameters from design plan
radius = 11.938  # mm
height = 12.7    # mm
center_x = 8.077681
center_y = 8.284339

# Build the part
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(height)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
