import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer dimensions: 1980 mm x 600 mm (from outer ring)
# Inner dimensions: 1930 mm x 550 mm (from inner ring)
# Extrude distance: 25 mm in +w direction (which is +y in world coordinates)

# Build the outer rectangle (closed wire)
outer = (
    cq.Workplane("XY")
    .moveTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .lineTo(-2.5, 57.5)
    .close()
    .wire()
)

# Build the inner rectangle (closed wire)
inner = (
    cq.Workplane("XY")
    .moveTo(0.0, 0.0)
    .lineTo(193.0, 0.0)
    .lineTo(193.0, 55.0)
    .lineTo(0.0, 55.0)
    .close()
    .wire()
)

# Combine into a single planar face with a hole
# We create the outer face, then cut the inner face
result = (
    cq.Workplane("XY")
    .placeSketch(outer, inner)
    .extrude(25.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0001\\neg_01/generated.step")
