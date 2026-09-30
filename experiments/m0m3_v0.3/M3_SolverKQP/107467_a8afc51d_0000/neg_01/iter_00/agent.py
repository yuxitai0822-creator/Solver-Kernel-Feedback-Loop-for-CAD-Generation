import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk) with radius 3.0 mm and extrude distance 14.0 mm
# The previous script incorrectly used 21.0 mm (perturbed value) instead of 14.0 mm
# Also the previous script had complex loop handling that is unnecessary for a simple circle

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0000\neg_01\iter_00/generated.step"

# Create a simple disk: circle radius 3.0 mm, extruded 14.0 mm in +Z direction
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan
    .extrude(14.0)  # extrude distance from design plan
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
