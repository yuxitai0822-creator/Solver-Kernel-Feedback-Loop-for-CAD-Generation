import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle: 40mm x 40mm (from u: 6 to 10, v: -7 to -3, scaled by 10)
# Inner rectangle: 37.6mm x 37.6mm (from u: 6.12 to 9.88, v: -6.88 to -3.12, scaled by 10)
# Extrude 780mm in the +w direction (which is +y in world coordinates)

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(40.0, 40.0)
    .extrude(780.0)
)

# Build the inner rectangle (the hole)
inner = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(37.6, 37.6)
    .extrude(780.0)
)

# Subtract inner from outer to create the frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0000\\neg_01/generated.step")
