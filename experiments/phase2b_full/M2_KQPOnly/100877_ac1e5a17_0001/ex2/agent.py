import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# Note: The design plan uses cm->mm conversion (x10), so values are already in mm.
# The profile is a rectangle with corners at (0,0), (27.94,0), (27.94,21.59), (0,21.59) in UV space.
# However, the dimensions table says length_u=279.4, width_v=215.9, which is 10x the UV values.
# This suggests the UV coordinates are in cm and need scaling to mm.
# We'll build the rectangle using the explicit dimensions from the dimensions table.

# Create a rectangle profile in the XY plane (u=x, v=y)
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)  # length_u along X, width_v along Y
    .extrude(1.5875)      # extrude along Z (positive direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\100877_ac1e5a17_0001\ex2/generated.step")
