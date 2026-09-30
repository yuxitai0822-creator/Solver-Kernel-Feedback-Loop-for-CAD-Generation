import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 50mm x 30mm (in UV plane)
# Inner rectangle: 40mm x 20mm (offset 5mm from outer edges)
# Extrude 500mm in +w direction

# Build the outer rectangle
outer = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
)

# Build the inner rectangle (hole)
inner = (
    cq.Workplane("XY")
    .rect(40.0, 20.0)
)

# Create the frame profile by subtracting inner from outer
# We need to center both rectangles at origin
result = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
    .pushPoints([(0, 0)])
    .rect(40.0, 20.0)
    .extrude(500.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104453_aba0f2d1_0006\\neg_01/generated.step")
