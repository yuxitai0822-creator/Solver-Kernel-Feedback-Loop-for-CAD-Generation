import cadquery as cq

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm (from cm to mm conversion applied)

# Create the rectangular plate
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\100877_ac1e5a17_0001\neg_01/generated.step")
