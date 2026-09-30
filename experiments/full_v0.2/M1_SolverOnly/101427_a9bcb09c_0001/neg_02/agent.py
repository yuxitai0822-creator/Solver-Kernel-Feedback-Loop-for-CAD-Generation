import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle: from (-2.5, -2.5) to (195.5, 57.5) in UV plane
# Inner rectangle: from (0, 0) to (193, 55) in UV plane
# Extrude 25 mm in +w direction (which is +Y in world coordinates)

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .moveTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .lineTo(-2.5, 57.5)
    .close()
)

# Build the inner rectangle (hole)
inner = (
    cq.Workplane("XY")
    .moveTo(0, 0)
    .lineTo(193, 0)
    .lineTo(193, 55)
    .lineTo(0, 55)
    .close()
)

# Combine: outer rectangle with inner hole, then extrude
result = (
    cq.Workplane("XY")
    .polyline([(-2.5, -2.5), (195.5, -2.5), (195.5, 57.5), (-2.5, 57.5)])
    .close()
    .polyline([(0, 0), (193, 0), (193, 55), (0, 55)])
    .close()
    .extrude(25.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101427_a9bcb09c_0001\\neg_02/generated.step")
