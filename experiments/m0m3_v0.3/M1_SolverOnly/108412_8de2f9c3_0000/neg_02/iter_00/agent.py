import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Stock - flat rectangular plate
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The perturbation description indicates the original length was 243.84 (cm) and perturbed to 292.608 (cm)
# which corresponds to 2926.08 mm. However, the design plan specifies 2438.4 mm for length_u.
# We'll follow the design plan dimensions exactly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108412_8de2f9c3_0000\neg_02\iter_00\generated.step"

# Dimensions from design plan (in mm)
length_u = 2438.4  # along x-axis
width_v = 1219.2   # along y-axis
extrude_distance = 12.7  # along z-axis

# Create the rectangular plate centered at origin
# The profile coordinates from the design plan show:
# start_uv: [121.92, -60.96] to [121.92, 60.96] etc.
# These are in cm (original units), so multiply by 10 to get mm:
# 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm
# This gives a rectangle of size 2438.4 x 1219.2 mm

result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
importers.export(result, OUT_STEP_PATH)
