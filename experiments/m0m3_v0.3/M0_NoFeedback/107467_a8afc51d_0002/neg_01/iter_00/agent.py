import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Pivot - a disk (extruded circle)
# Dimensions: radius = 3.0 mm, extrude distance = 25.0 mm
# The previous script had incorrect extrude distance (37.5 mm instead of 25.0 mm)
# and unnecessarily complex loop handling for a simple circle.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0002\neg_01\iter_00\generated.step"

# Create a simple disk: circle radius 3.0 mm, extruded 25.0 mm in +Z direction
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan: 3.0 mm
    .extrude(25.0)  # extrude distance from design plan: 25.0 mm
)

# Export to STEP
importers = None  # not needed
exporters.export(result, OUT_STEP_PATH)
