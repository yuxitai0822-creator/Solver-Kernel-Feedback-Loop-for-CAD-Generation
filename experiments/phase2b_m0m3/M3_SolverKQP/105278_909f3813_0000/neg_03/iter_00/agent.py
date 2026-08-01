import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\105278_909f3813_0000\neg_03\iter_00/generated.step"

# Design Plan: rectangular prism with dimensions 12mm x 60mm x 40mm
# The profile is a rectangle centered at origin in the XZ plane
# Extrude along Y axis (positive direction) by 40mm

# Create the base workplane on XZ plane
base_wp = cq.Workplane("XZ")

# Create the rectangle profile: width=12mm along X, height=60mm along Z
# Center at origin
profile = base_wp.center(0, 0).rect(12.0, 60.0, centered=True)

# Extrude along Y axis (positive direction) by 40mm
result = profile.extrude(40.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
