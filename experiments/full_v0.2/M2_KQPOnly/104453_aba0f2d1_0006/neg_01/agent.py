import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle: 50mm x 30mm (from UV coordinates: 0,0 to 50,30)
# Inner rectangle: 40mm x 20mm (from UV coordinates: 5,5 to 45,25)
# Extrude 500mm in the +w direction (z-axis)

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .rect(50, 30)
)

# Build the inner rectangle (the hole)
inner = (
    cq.Workplane("XY")
    .rect(40, 20)
)

# Create the frame by extruding the outer rectangle and cutting the inner rectangle
result = (
    cq.Workplane("XY")
    .rect(50, 30)
    .extrude(500)
    .faces("<Z")
    .workplane()
    .rect(40, 20)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104453_aba0f2d1_0006\\neg_01/generated.step")
