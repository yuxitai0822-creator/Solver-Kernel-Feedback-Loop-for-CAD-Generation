import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the XY plane
# Extrude in +Z direction by 2.5 mm

# Build the rectangle profile (centered at origin)
result = (
    cq.Workplane("XY")
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0004\neg_01\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)