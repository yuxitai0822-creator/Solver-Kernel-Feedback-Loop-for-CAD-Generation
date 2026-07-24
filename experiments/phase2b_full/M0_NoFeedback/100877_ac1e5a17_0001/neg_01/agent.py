import cadquery as cq

# Design Plan: Backing v1
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm_to_mm conversion (x10), so the values are already in mm.
# The profile is a rectangle with corners at (0,0), (27.94,0), (27.94,21.59), (0,21.59) in UV space.
# However, the dimensions table says length_u = 279.4 and width_v = 215.9, which are 10x the UV values.
# This suggests the UV coordinates are in cm and need scaling to mm.
# We'll use the explicit dimensions from the dimensions table: 279.4 x 215.9 x 1.5875 mm.

# Create the rectangular plate
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\100877_ac1e5a17_0001\neg_01/generated.step")
