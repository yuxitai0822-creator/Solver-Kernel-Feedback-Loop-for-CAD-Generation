import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 50mm x 30mm (in UV plane)
# Inner rectangle: 40mm x 20mm (offset 5mm from outer edges)
# Extrude 500mm in +w direction

# Create the outer rectangle profile
outer = (
    cq.Workplane("XY")
    .moveTo(0, 0)
    .lineTo(50, 0)
    .lineTo(50, 30)
    .lineTo(0, 30)
    .close()
)

# Create the inner rectangle profile (hole)
inner = (
    cq.Workplane("XY")
    .moveTo(5, 5)
    .lineTo(45, 5)
    .lineTo(45, 25)
    .lineTo(5, 25)
    .close()
)

# Combine: outer minus inner to create the frame profile
frame_profile = outer.cut(inner)

# Extrude the frame profile by 500mm in the +Z direction (which is +w)
result = frame_profile.extrude(500.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0006\\neg_03/generated.step")
