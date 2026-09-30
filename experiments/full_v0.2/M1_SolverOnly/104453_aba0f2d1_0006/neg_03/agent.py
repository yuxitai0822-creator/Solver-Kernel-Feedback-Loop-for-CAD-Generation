import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle: 50mm x 30mm (from UV coordinates: 0,0 to 50,30)
# Inner rectangle: 40mm x 20mm (from UV coordinates: 5,5 to 45,25)
# Extrude 500mm in the +w direction (z-axis)

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
)

# Build the inner rectangle (the hole)
inner = (
    cq.Workplane("XY")
    .rect(40.0, 20.0)
)

# Create the frame profile by cutting inner from outer
# We need to center the rectangles at the origin
# Outer: center at (0,0) with width 50, height 30
# Inner: center at (0,0) with width 40, height 20
# This matches the UV coordinates: outer from (0,0) to (50,30), inner from (5,5) to (45,25)

result = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
    .extrude(500.0)
    .faces("<Z")
    .workplane()
    .rect(40.0, 20.0)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104453_aba0f2d1_0006\\neg_03/generated.step")
