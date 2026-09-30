import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 50mm x 30mm (from profile curves)
# Inner rectangle: 40mm x 20mm (from profile curves, offset 5mm from edges)
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

# Create the inner rectangle profile (cutout)
inner = (
    cq.Workplane("XY")
    .moveTo(5, 5)
    .lineTo(45, 5)
    .lineTo(45, 25)
    .lineTo(5, 25)
    .close()
)

# Build the frame by extruding the outer profile and cutting the inner profile
result = (
    cq.Workplane("XY")
    .polyline([(0, 0), (50, 0), (50, 30), (0, 30)])
    .close()
    .extrude(500.0)
    .faces("<Z")
    .workplane()
    .polyline([(5, 5), (45, 5), (45, 25), (5, 25)])
    .close()
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104453_aba0f2d1_0006\\neg_02/generated.step")
