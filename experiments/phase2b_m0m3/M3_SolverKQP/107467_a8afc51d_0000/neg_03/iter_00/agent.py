import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0000\neg_03\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 3.0 mm
# - Extrude distance: 14.0 mm in +w direction (which is +Z)
# - No inner holes (the previous script incorrectly added an inner loop)
# - Body count: 1

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius 3.0 mm
    .extrude(14.0)        # extrude 14.0 mm in +Z
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
