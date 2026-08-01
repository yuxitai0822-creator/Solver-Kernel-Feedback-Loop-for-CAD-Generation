import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin, with half-widths 4.25 and 9.0
# Extrude in +Z direction by 2.5 mm

# Build the rectangle profile on the XY plane
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0004\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)