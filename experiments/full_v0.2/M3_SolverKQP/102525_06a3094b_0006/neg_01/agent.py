import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the origin in the XY plane, extruded in +Z direction.

# Create rectangle profile centered at origin
# length_u = 11.3 mm (along X), width_v = 21.0 mm (along Y)
result = (
    cq.Workplane("XY")
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0006\\neg_01/generated.step")
