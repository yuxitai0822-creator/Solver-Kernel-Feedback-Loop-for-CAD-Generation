import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Tail Stock Lever - a simple disk (extruded circle)
# Dimensions:
#   Radius: 11.938 mm (from profiles[0].radius.value)
#   Extrude distance: 12.7 mm (from extrude.distance_total.value)
#   Center UV: (8.077681, 8.284339) - used for positioning
#
# The previous script had issues:
# 1. It tried to load a history JSON file that may not exist
# 2. It had complex multi-loop logic for a simple disk
# 3. It incorrectly included an inner loop (hole) when the design plan specifies only an outer circle
# 4. The OUT_STEP path was not properly set
#
# This script creates a simple cylinder (extruded circle) matching the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0004\neg_03\iter_00\generated.step"

# Parameters from design plan
radius = 11.938  # mm
height = 12.7    # mm
center_x = 8.077681
center_y = 8.284339

# Build the part: a simple disk (cylinder)
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(height)
)

# Export to STEP
importers.export(result, OUT_STEP_PATH)
