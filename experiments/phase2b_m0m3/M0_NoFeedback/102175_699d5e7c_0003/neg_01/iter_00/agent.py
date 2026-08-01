import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism with dimensions 39.0 x 68.0 x 10.0 mm
# The profile is a rectangle from (-3.9, 6.8) to (0.0, 0.0) in UV space
# After unit conversion (cm to mm x10), this becomes (-39.0, 68.0) to (0.0, 0.0)
# Extrude distance is 10.0 mm (from design plan, not the perturbed 15.0)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

# Build the rectangle profile
# The rectangle corners in UV space: (-3.9, 0.0), (0.0, 0.0), (0.0, 6.8), (-3.9, 6.8)
# After cm->mm conversion: (-39.0, 0.0), (0.0, 0.0), (0.0, 68.0), (-39.0, 68.0)
# Width = 39.0 mm, Height = 68.0 mm

# Create workplane and draw rectangle
result = (cq.Workplane("XY")
    .moveTo(-39.0, 0.0)
    .lineTo(0.0, 0.0)
    .lineTo(0.0, 68.0)
    .lineTo(-39.0, 68.0)
    .close()
    .extrude(10.0)  # Extrude 10.0 mm in +Z direction
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
