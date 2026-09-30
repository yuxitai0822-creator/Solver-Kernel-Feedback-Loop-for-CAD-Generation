import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The design plan specifies a rectangle of 254.0 mm x 190.5 mm extruded to 3.175 mm
# Note: The profile curves in the design plan show coordinates 0-25.4 and 0-19.05,
# but the explicit dimensions state 254.0 x 190.5. The curves appear to be in cm (scaled by 10x).
# We use the explicit dimensions: length_u=254.0, width_v=190.5, extrude=3.175

result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100877_ac1e5a17_0017\\neg_02/generated.step")
