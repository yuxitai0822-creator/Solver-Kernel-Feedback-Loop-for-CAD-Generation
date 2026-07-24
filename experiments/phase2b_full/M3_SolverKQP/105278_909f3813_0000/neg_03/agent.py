import cadquery as cq

# Create a rectangular prism with dimensions: length_u=12mm, width_v=60mm, extrude_distance=40mm
# The profile is a rectangle centered at the origin in the XY plane, extruded in the +Z direction.

# Define the rectangle dimensions
length_u = 12.0  # along X (u direction)
width_v = 60.0   # along Y (v direction)
extrude_distance = 40.0  # along Z (w direction)

# Build the result: rectangle centered at origin, extruded upward
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\105278_909f3813_0000\\neg_03/generated.step")
