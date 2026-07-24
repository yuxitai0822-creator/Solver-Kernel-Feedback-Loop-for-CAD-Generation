import cadquery as cq

# Create a rectangular prism with dimensions: length_u=3.9, width_v=4.9, extrude_distance=1.55
# The profile is a rectangle centered at origin in the XY plane, extruded in the +Z direction

# Define the rectangle dimensions
length_u = 3.9  # along X axis
width_v = 4.9   # along Y axis
extrude_distance = 1.55  # along Z axis

# Create the rectangle profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0000\\neg_02/generated.step")
