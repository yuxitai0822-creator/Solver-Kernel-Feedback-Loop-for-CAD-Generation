import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Tail Stock Lever - a simple disk (extruded circle)
# Dimensions: radius = 11.938 mm, extrude distance = 12.7 mm
# The design plan specifies a single outer circle with no inner holes

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0004\neg_03\iter_00\generated.step"

# Create the base workplane
result = cq.Workplane("XY")

# According to the design plan:
# - Profile: single circle with radius 11.938 mm
# - Center in UV coordinates: (8.077681, 8.284339)
# - Extrude distance: 12.7 mm in +w direction (which is +Z)

# Move to the center point and create the circle
result = result.moveTo(8.077681, 8.284339).circle(11.938)

# Extrude to create the solid disk
result = result.extrude(12.7)

# Export the result
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
