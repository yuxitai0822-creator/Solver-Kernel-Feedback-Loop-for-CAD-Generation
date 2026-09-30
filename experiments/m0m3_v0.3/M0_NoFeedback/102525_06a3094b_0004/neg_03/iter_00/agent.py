import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0004\neg_03\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin, with u-span=8.5 (along x) and v-span=18.0 (along y)
# Extrude along w (z) direction by 2.5 mm

# Build the rectangle profile on XY plane
result = (
    cq.Workplane("XY")
    .rect(8.5, 18.0, centered=True)  # width=8.5 along x, height=18.0 along y
    .extrude(2.5)  # extrude along +z by 2.5 mm
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
