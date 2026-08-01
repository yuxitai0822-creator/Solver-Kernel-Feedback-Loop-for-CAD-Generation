import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude_distance = 3.175 mm
# The profile is a rectangle with corners at (0,0), (25.4,0), (25.4,19.05), (0,19.05) in UV space
# Note: The design plan shows UV coordinates that are 1/10 of the actual dimensions because
# the original was in cm and converted to mm. The actual dimensions are 254.0 x 190.5 mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_02\iter_00\generated.step"

# Create the rectangular plate
# Using the dimensions from the design plan: 254.0 mm x 190.5 mm x 3.175 mm
length_u = 254.0  # mm
width_v = 190.5   # mm
extrude_distance = 3.175  # mm

# Build the plate centered on the XY plane for simplicity
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
