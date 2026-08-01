import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0004\neg_03\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 8.5mm x 18.0mm x 2.5mm
# The profile is a rectangle centered at origin in the XY plane
# Extrude in +Z direction by 2.5mm

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Create rectangle centered at origin with width=8.5 (along X) and height=18.0 (along Y)
# Note: rect(width, height) creates a rectangle centered at the current point
profile = wp.center(0, 0).rect(8.5, 18.0)

# Extrude in +Z direction by 2.5mm
result = profile.extrude(2.5)

# Export to STEP file
exporters.export(result, OUT_STEP_PATH)
