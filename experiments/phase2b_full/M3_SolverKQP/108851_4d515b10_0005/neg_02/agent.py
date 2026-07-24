import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 307.848 mm and width_v = 19.05 mm
# Extrude distance = 12.7 mm in the +w direction

# Define the rectangle dimensions
length_u = 307.848  # mm
width_v = 19.05     # mm
extrude_distance = 12.7  # mm

# Create the rectangular profile on the XY plane (u=x, v=y, w=z)
# The profile is centered at the origin for simplicity
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export the result to STEP file
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0005\\neg_02/generated.step")
