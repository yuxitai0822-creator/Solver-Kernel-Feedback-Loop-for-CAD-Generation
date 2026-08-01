import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm (extruded rectangle)
# The perturbation changes the x-dimension from 27.94 to 33.528 (in cm?)
# But the design plan says length_u = 279.4 mm, width_v = 215.9 mm
# The previous script had incorrect coordinates; we'll build from scratch

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0001\neg_02\iter_00\generated.step"

# Build the rectangular plate centered at origin
# Dimensions from design plan:
length_u = 279.4  # mm (along x)
width_v = 215.9   # mm (along y)
extrude_dist = 1.5875  # mm (along z)

# Create workplane and draw rectangle centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
