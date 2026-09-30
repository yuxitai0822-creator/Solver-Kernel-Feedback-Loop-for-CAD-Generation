import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\105278_909f3813_0000\neg_01\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 12mm x 60mm x 40mm
# The profile is a rectangle in the XZ plane, extruded along Y
# Rectangle dimensions: u=12mm (along X), v=60mm (along Z)
# Extrude distance: 40mm along Y (w direction)

# Create workplane on XZ plane (Y is normal)
wp = cq.Workplane("XZ")

# Build the rectangle centered at origin
# Rectangle width = 12mm (along X), height = 60mm (along Z)
result = wp.rect(12.0, 60.0, centered=True).extrude(40.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
