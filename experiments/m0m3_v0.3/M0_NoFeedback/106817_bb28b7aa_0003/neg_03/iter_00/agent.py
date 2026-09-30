import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk) with radius 4.7117 mm, extrude 12.192 mm
# The previous script had an inner loop (hole) that should NOT be present.
# The design plan specifies a single solid body (disk) with no holes.
# We remove the inner loop and simplify to a single circle extrusion.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0003\neg_03\iter_00/generated.step"

# Parameters from design plan
radius = 4.7117  # mm
extrude_height = 12.192  # mm
center_x = 50.800002
center_y = 63.500002

# Build the disk: circle extruded along Y axis (since WORKPLANE='XZ' in original)
# Using XY plane for simplicity, then extrude in Z
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_height)
)

exporters.export(result, OUT_STEP_PATH)
