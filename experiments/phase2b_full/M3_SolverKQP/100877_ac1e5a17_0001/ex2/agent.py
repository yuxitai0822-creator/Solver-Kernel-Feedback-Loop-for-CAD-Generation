import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm->mm conversion (x10), so values are already in mm.
# The profile is a rectangle with corners at (0,0), (27.94,0), (27.94,21.59), (0,21.59) in UV space.
# However, the dimensions table says length_u=279.4 and width_v=215.9, which are 10x the UV values.
# This is because the UV coordinates are in cm (original source) and the dimensions are in mm after conversion.
# We use the explicit dimensions from the design plan: 279.4 mm x 215.9 mm x 1.5875 mm.

# Build the plate centered at origin for better STEP export
length_u = 279.4
width_v = 215.9
thickness = 1.5875

result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(thickness)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\100877_ac1e5a17_0001\ex2/generated.step")
