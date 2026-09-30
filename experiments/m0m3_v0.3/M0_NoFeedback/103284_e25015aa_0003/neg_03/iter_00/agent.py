import cadquery as cq
from cadquery import exporters
import math

# Design Plan: single disk (extruded circle)
# Dimensions:
#   radius = 25.4 mm (from profiles[0].radius.value)
#   extrude distance = 8.89 mm (from extrude.distance_total.value)
#   center_uv = (16.994661, 17.998557) - but we place at origin for simplicity
#   The design plan shows a simple disk with no inner holes (only 1 outer loop, no inner loops)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0003\neg_03\iter_00/generated.step"

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius from design plan
    .extrude(8.89)  # height from design plan
)

# Export
importers = None  # not needed
exporters.export(result, OUT_STEP_PATH)
