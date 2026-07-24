import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 50mm x 30mm (from profile curves)
# Inner rectangle: 40mm x 20mm (from profile curves, 5mm offset from outer)
# Extrude distance: 500mm along +w (z-axis)

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

# Combine: outer rectangle with inner rectangle subtracted to form a frame
frame_profile = outer.cut(inner)

# Extrude the frame profile by 500mm along the z-axis (positive direction)
result = frame_profile.extrude(500.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0006\\ex2/generated.step")
