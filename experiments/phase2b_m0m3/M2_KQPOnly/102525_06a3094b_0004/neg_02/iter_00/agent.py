import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0004\neg_02\iter_00/generated.step"

# Design Plan: rectangular prism 8.5 x 18.0 x 2.5 mm
# The profile rectangle is centered at origin in UV plane.
# U direction = X axis, V direction = Z axis (negative), W direction = Y axis
# Extrude in +W direction (Y axis) by 2.5 mm

# Build the rectangle on the XZ plane (since V is along Z, U along X)
# Rectangle dimensions: length_u = 8.5 (along X), width_v = 18.0 (along Z)
# Center at origin
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)  # extrude along Y (positive direction)
)

exporters.export(result, OUT_STEP_PATH)
