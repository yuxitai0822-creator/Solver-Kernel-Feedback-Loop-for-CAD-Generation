import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the origin in the XY plane, extruded in +Z direction.

# Create the rectangle profile centered at origin
# Width along X = 11.3mm, length along Y = 21.0mm
result = (
    cq.Workplane("XY")
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102525_06a3094b_0006\neg_03/generated.step")
