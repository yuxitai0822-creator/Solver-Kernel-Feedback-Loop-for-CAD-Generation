import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u direction) = 254.0 mm, Width (v direction) = 190.5 mm, Thickness (w direction) = 3.175 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\100877_ac1e5a17_0017\\neg_01/generated.step")
