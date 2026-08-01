import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm (extrude depth)
# The perturbation description mentions E2_extrude_depth with original=0.15875, perturbed=0.238125
# but the design plan explicitly states extrude_distance = 1.5875 mm (which is 0.15875 cm * 10)
# We follow the design plan exactly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0001\neg_01\iter_00/generated.step"

# Rectangle dimensions from design plan profiles[0]
length_u = 279.4  # mm (along x)
width_v = 215.9   # mm (along y)
extrude_depth = 1.5875  # mm (along z)

# Build the plate centered on XY plane for simplicity
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_depth)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
