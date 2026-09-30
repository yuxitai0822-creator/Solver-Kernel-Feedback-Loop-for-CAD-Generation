import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 254.0 mm, Width (v) = 190.5 mm, Extrude distance (w) = 3.175 mm
# Note: The design plan uses a coordinate system where u=x, v=y, w=z
# The profile curves show a rectangle from (0,0) to (25.4, 19.05) in uv space
# but the dimensions table says 254.0 x 190.5 mm. The curves appear to be in cm
# (since compiler notes say cm_to_mm x10). So we use the explicit dimensions.

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100877_ac1e5a17_0017\\neg_03/generated.step")
