import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 209.55 mm, width_v = 57.912 mm, extrude_distance = 19.05 mm
# The profile is a rectangle in the UV plane, extruded along the W direction

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0009\\neg_02/generated.step")
