import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of 193.0 mm x 55.0 mm (note: dimensions in plan are 1930.0 and 550.0 but curves show 193.0 and 55.0)
# The extrude distance is 50.0 mm

# Create the rectangle profile on the XY plane
result = (
    cq.Workplane("XY")
    .rect(193.0, 55.0)
    .extrude(50.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0002\\neg_01/generated.step")
