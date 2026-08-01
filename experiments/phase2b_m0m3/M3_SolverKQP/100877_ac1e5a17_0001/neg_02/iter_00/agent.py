import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0001\neg_02\iter_00/generated.step"

# Design Plan dimensions (in mm)
# Rectangle: length_u = 279.4, width_v = 215.9
# Extrude distance = 1.5875
# Note: The perturbation description says original=27.94, perturbed=33.528
# but the design plan clearly states length_u=279.4 (which is 10x 27.94 due to cm->mm conversion)
# The perturbed value 33.528 would be 10x 3.3528, but the design plan says 279.4
# We follow the design plan exactly as specified.

length_u = 279.4  # mm (from design plan)
width_v = 215.9   # mm (from design plan)
extrude_distance = 1.5875  # mm (from design plan)

# Build the part using cadquery
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
importers = None
exporters.export(result, OUT_STEP_PATH)
