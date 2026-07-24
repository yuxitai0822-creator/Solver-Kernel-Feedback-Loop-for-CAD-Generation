import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The design plan specifies a rectangle of 254.0 mm x 190.5 mm extruded to 3.175 mm
# Note: The profile curves show 25.4 x 19.05 which is 1/10 of the actual dimensions
# This is because the design plan notes unit_conversion_applied: cm_to_mm (x10)
# So the actual dimensions are 254.0 mm x 190.5 mm x 3.175 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100877_ac1e5a17_0017\\ex2/generated.step")
