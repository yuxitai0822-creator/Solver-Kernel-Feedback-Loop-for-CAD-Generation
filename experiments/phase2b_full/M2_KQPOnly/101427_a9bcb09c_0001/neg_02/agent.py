import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: from (-2.5, -2.5) to (195.5, 57.5) in UV plane
# Inner rectangle: from (0, 0) to (193.0, 55.0) in UV plane
# Extrude in +w direction by 25.0 mm

# Create the outer rectangle
outer = (
    cq.Workplane("XY")
    .moveTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .lineTo(-2.5, 57.5)
    .close()
)

# Create the inner rectangle (cutout)
inner = (
    cq.Workplane("XY")
    .moveTo(0.0, 0.0)
    .lineTo(193.0, 0.0)
    .lineTo(193.0, 55.0)
    .lineTo(0.0, 55.0)
    .close()
)

# Combine: outer profile with inner hole, then extrude
result = (
    cq.Workplane("XY")
    .add(outer)
    .cut(inner)
    .extrude(25.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0001\\neg_02/generated.step")
