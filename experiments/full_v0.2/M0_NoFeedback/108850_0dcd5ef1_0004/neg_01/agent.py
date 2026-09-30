import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions: length_u = 171.45 mm, width_v = 110.998 mm, extrude_distance = 6.35 mm
# The profile is a rectangle in the UV plane, extruded along the W direction

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(171.45, 110.998)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108850_0dcd5ef1_0004\\neg_01/generated.step")
