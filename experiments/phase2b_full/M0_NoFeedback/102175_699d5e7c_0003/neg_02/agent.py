import cadquery as cq

# Create a rectangular prism with dimensions 39mm x 68mm x 10mm
# The profile is a rectangle in the XY plane, extruded in the Z direction
# Note: The design plan uses a coordinate system where the rectangle spans from
# u=-3.9 to u=0 and v=0 to v=6.8, but the dimensions are 39mm x 68mm.
# This suggests the UV coordinates are in cm (since 3.9cm = 39mm, 6.8cm = 68mm).
# We'll build the part centered at the origin for simplicity.

result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102175_699d5e7c_0003\\neg_02/generated.step")
