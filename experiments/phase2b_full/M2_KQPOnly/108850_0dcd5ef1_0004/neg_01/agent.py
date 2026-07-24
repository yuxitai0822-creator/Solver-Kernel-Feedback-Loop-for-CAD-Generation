import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: 171.45 mm x 110.998 mm x 6.35 mm
# The coordinate system uses u along x, v along z (negative), w along y
# We'll build the rectangle in the XY plane and extrude along Z for simplicity
# but to match the frame orientation (u=x, v=-z, w=y), we can rotate later if needed.
# Since the part is a flat plate, orientation is not critical for shape.

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(171.45, 110.998)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108850_0dcd5ef1_0004\\neg_01/generated.step")
