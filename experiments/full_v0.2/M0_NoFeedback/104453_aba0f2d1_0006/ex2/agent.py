import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 50mm x 30mm (in UV plane)
# Inner rectangle: 40mm x 20mm (offset 5mm from edges)
# Extrude 500mm in +w direction

# Create the outer rectangle
outer = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
    .extrude(500.0)
)

# Create the inner rectangle (to be subtracted)
inner = (
    cq.Workplane("XY")
    .rect(40.0, 20.0)
    .extrude(500.0)
)

# Position inner rectangle centered within outer (offset 5mm from each edge)
# Outer rect: center at (0,0), spans -25 to 25 in X, -15 to 15 in Y
# Inner rect: center at (0,0), spans -20 to 20 in X, -10 to 10 in Y
# This gives 5mm wall thickness on all sides

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104453_aba0f2d1_0006\\ex2/generated.step")
