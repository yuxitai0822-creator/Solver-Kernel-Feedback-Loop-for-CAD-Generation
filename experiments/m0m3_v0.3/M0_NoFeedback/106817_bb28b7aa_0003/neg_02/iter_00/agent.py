import cadquery as cq
from cadquery import exporters
import math

# Design Plan: ruler holder w/screw - disk with extruded circle
# Dimensions:
#   Circle radius: 4.7117 mm (from design plan dimensions.profiles[0].radius)
#   Extrude distance: 12.192 mm
#   Circle center in UV: (50.800002, 63.500002) - but we center at origin for simplicity

# Build the part
result = (
    cq.Workplane("XZ")  # Using XZ plane as per original script
    .circle(4.7117)      # Radius from design plan
    .extrude(12.192)     # Extrude distance from design plan
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0003\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)