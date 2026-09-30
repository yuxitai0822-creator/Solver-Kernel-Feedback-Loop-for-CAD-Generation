import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: length_u = 279.4 mm, width_v = 215.9 mm, extrude_distance = 1.5875 mm
# The perturbation changes the length from 27.94 to 33.528 (in some unit), but the design plan
# specifies 279.4 mm (which is 27.94 cm converted to mm). We'll use the design plan values.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0001\neg_02\iter_00/generated.step"

# Create the rectangular plate
# The rectangle is centered at origin for simplicity, then extruded
length_u = 279.4  # mm (along x-axis)
width_v = 215.9   # mm (along y-axis)
extrude_distance = 1.5875  # mm (along z-axis)

# Build the part
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
