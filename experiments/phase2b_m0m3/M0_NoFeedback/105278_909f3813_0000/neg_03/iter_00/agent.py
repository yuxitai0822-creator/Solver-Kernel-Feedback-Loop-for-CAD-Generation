import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\105278_909f3813_0000\neg_03\iter_00/generated.step"

# Design Plan: rectangular prism with dimensions 12mm x 60mm x 40mm
# The profile is a rectangle centered at origin in the XZ plane
# Extrude along Y axis (positive direction) by 40mm

# Rectangle dimensions from design plan:
# length_u = 12.0 mm (along X axis)
# width_v = 60.0 mm (along Z axis)
# extrude_distance = 40.0 mm (along Y axis)

# Create workplane on XZ plane (Y normal)
wp = cq.Workplane("XZ")

# Create centered rectangle: width=12 along X, height=60 along Z
# Note: rect(width, height) creates rectangle centered at current point
result = wp.rect(12.0, 60.0, centered=True).extrude(40.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
