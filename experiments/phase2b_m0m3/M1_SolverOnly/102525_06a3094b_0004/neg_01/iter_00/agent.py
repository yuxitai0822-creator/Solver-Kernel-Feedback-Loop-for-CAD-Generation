import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin, with width 8.5 (along u) and height 18.0 (along v)
# Extrude 2.5 mm in the +w direction (which maps to +Y in cadquery's default XY plane)

# Build the rectangle profile on the XY plane
result = (
    cq.Workplane("XY")
    .rect(8.5, 18.0, centered=True)  # width=8.5 (u), height=18.0 (v)
    .extrude(2.5)  # extrude 2.5 mm in +Z (which corresponds to +w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0004\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)