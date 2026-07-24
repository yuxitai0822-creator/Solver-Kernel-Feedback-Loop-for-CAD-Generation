import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the XY plane, extruded in the +Z direction.

# Create the rectangle profile centered at origin
# Length along X (u) = 11.3, Width along Y (v) = 21.0
# The profile is centered, so half-lengths are 5.65 and 10.5
result = (
    cq.Workplane("XY")
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0006\\neg_03/generated.step")
