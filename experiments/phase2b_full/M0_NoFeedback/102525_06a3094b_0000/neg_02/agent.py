import cadquery as cq

# Create a rectangular prism based on the design plan
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# The profile is centered at origin in the uv-plane, then extruded in +w direction

# Create the rectangle profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(3.9, 4.9)
    .extrude(1.55)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0000\\neg_02/generated.step")
