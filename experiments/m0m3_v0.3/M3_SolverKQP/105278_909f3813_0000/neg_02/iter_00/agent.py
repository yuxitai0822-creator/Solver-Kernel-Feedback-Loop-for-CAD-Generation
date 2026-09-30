import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 12mm x 60mm x 40mm (extruded rectangle)
# The profile is a rectangle centered at origin in the XZ plane, extruded along Y
# Dimensions: length_u=12mm (along X), width_v=60mm (along Z), extrude_distance=40mm (along Y)

# Build the rectangle profile on the XZ plane (Y is extrusion direction)
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(12.0, 60.0, centered=True)
    .extrude(40.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\105278_909f3813_0000\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)