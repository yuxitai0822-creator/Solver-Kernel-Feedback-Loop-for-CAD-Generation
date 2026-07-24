import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the UV plane, then extruded in the +W direction.
# Note: The design plan uses a coordinate system where the rectangle spans from u=-3.9 to u=0.0 and v=0.0 to v=6.8.
# However, the dimensions indicate length_u=39.0 and width_v=68.0, which suggests the UV coordinates are in cm (since the plan notes cm_to_mm x10).
# We will build the part in mm using the explicit dimensions: 39.0 mm x 68.0 mm x 10.0 mm.
# The rectangle is placed in the XY plane, centered at the origin for simplicity, then extruded along Z.

result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102175_699d5e7c_0003\\neg_03/generated.step")
