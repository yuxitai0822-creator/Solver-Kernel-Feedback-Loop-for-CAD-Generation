import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm
# The perturbation changes the y-dimension from 215.9 to 17.272 (but we follow the design plan)
# Actually, looking at the design plan, the width_v is 215.9, but the perturbation description says
# original=21.59, perturbed=17.272. This suggests the perturbation is on a different scale.
# The design plan explicitly states width_v = 215.9 (which is 21.59 * 10, consistent with cm->mm conversion).
# The perturbation changes 21.59 to 17.272, so in mm that would be 172.72.
# However, the design plan's explicit dimension is 215.9, so we must follow the design plan.
# The previous script used 194.31 and 21.59 which doesn't match the design plan.
# We'll create a clean script matching the design plan exactly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0001\neg_03\iter_00/generated.step"

# Create the rectangular plate
# Using the design plan dimensions:
# length_u = 279.4 mm (along x)
# width_v = 215.9 mm (along y)
# extrude_distance = 1.5875 mm (along z)

result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9, centered=True)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
