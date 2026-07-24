import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Profile rectangle: u from 0 to 95.25, v from 0 to 571.5
# Extrude in +w direction by 19.05 mm

result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101269_f084ba14_0023\\neg_01/generated.step")
