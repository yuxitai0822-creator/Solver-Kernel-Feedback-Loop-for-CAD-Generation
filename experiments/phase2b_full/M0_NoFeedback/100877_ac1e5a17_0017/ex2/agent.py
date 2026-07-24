import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude distance = 3.175 mm
# Note: The design plan uses a local frame with u=x, v=y, w=z.
# The rectangle profile is defined in UV space with coordinates:
#   (0.0, 19.05) -> (0.0, 0.0) -> (25.4, 0.0) -> (25.4, 19.05) -> (0.0, 19.05)
# This is a 25.4 x 19.05 rectangle in UV space, but the dimensions table says 254.0 x 190.5.
# The compiler note says "cm_to_mm (x10)" was applied, so the UV coordinates are in cm originally.
# We scale by 10 to get mm: 25.4*10 = 254.0, 19.05*10 = 190.5.
# We'll build the rectangle directly at the correct mm dimensions.

# Create the rectangle profile in the XY plane (u=x, v=y)
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100877_ac1e5a17_0017\\ex2/generated.step")
