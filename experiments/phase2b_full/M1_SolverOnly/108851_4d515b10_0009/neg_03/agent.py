import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 209.55 mm, width_v = 57.912 mm, extrude_distance = 19.05 mm
# The profile is a rectangle in the UV plane, extruded along the W direction

# Define the rectangle dimensions
length_u = 209.55  # mm
width_v = 57.912   # mm
extrude_distance = 19.05  # mm

# Create the rectangular profile on the XY plane (UV plane)
# The rectangle is centered at the origin for simplicity
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0009\\neg_03/generated.step")
