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

# Create the frame profile by cutting the inner from the outer
# We need to center the rectangles at the origin
# Outer rect centered at (25, 15) in UV space, so we offset to center at origin
result = (
    cq.Workplane("XY")
    .rect(50.0, 30.0)
    .rect(40.0, 20.0)
    .extrude(500.0)
)

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104453_aba0f2d1_0006\\ex2/generated.step")
