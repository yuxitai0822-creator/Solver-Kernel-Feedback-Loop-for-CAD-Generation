import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism, 39.0 x 68.0 x 10.0 mm
# The profile rectangle is defined in UV coordinates with:
#   u range: [-3.9, 0.0]  (width = 3.9 cm = 39.0 mm)
#   v range: [0.0, 6.8]   (height = 6.8 cm = 68.0 mm)
# Extrude distance: 10.0 mm in +w direction

# Build the rectangle on the XY plane (which corresponds to UV plane)
# Using centered rectangle for simplicity: width=39.0, height=68.0
result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102175_699d5e7c_0003\neg_03\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)