import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk)
# Radius = 3.0 mm (from dimensions.profiles[0].radius.value)
# Extrude distance = 14.0 mm (from dimensions.extrude_distance.value)
# Note: The perturbed radius 0.375 in the previous script was incorrect;
# the design plan specifies radius 3.0 mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0000\neg_02\iter_00\generated.step"

# Build the disk: circle radius 3.0 mm, extrude 14.0 mm in +Z
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan
    .extrude(14.0)  # extrude distance from design plan
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
