import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0003\neg_02\iter_00/generated.step"

# Design Plan: extruded circle (disk)
# Profile: circle, center_uv = (1.6994660913961006, 1.7998556732836484), radius = 2.54
# Extrude: one_side, +w, distance = 8.89
# Note: The design plan's profile radius is 2.54, but the perturbation description says radius changed from 2.54 to 3.175.
# The previous script used radius 31.75 (which is 2.54*12.5? Actually 2.54*12.5=31.75, but that seems wrong).
# The design plan dimensions section says radius = 25.4 (which is 2.54*10). There is inconsistency.
# We follow the design plan's profile radius = 2.54 and extrude distance = 8.89.
# The center_uv in the design plan is (1.6994660913961006, 1.7998556732836484).
# We'll create a circle at that center with radius 2.54, then extrude 8.89 in +Z.

result = (
    cq.Workplane("XY")
    .moveTo(1.6994660913961006, 1.7998556732836484)
    .circle(2.54)
    .extrude(8.89)
)

exporters.export(result, OUT_STEP_PATH)
