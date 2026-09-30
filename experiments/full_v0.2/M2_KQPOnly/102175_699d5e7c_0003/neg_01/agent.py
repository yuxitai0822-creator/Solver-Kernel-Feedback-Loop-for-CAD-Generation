import cadquery as cq

# Create a rectangular prism with dimensions 39mm x 68mm x 10mm
# The profile is a rectangle in the XY plane, extruded in the Z direction
result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102175_699d5e7c_0003\\neg_01/generated.step")
