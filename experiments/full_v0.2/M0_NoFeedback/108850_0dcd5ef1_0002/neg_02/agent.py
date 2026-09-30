import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 171.45 mm, Width (v) = 38.1 mm, Extrude distance (w) = 6.35 mm
# The profile is defined in the uv-plane, then extruded in the +w direction

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108850_0dcd5ef1_0002\\neg_02/generated.step")
