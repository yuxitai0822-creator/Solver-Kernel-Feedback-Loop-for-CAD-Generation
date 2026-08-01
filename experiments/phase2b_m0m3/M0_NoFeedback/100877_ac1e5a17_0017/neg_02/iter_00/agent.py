import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude_distance = 3.175 mm
# The profile rectangle is defined in UV space with corners at:
# (0.0, 19.05), (0.0, 0.0), (25.4, 0.0), (25.4, 19.05)
# Note: The UV coordinates are in cm (as per compiler_notes: unit_conversion_applied = cm_to_mm x10)
# So we multiply by 10 to get mm: 25.4 cm = 254 mm, 19.05 cm = 190.5 mm

# Build the rectangle in the XY plane
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5, centered=True)
    .extrude(3.175)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100877_ac1e5a17_0017\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)