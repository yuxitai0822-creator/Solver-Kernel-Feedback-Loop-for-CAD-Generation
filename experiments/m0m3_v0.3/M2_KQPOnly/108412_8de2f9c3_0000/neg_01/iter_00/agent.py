import cadquery as cq
from cadquery import exporters
import math

# Design Plan: flat_plate_or_panel, extruded rectangle
# Dimensions: length_u=2438.4 mm, width_v=1219.2 mm, extrude_distance=12.7 mm
# The previous script used 19.05 mm (1.905 cm) which was the perturbed value.
# This script uses the correct design plan value of 12.7 mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108412_8de2f9c3_0000\neg_01\iter_00/generated.step"

# Rectangle dimensions from design plan (in mm)
length_u = 2438.4  # along x-axis
width_v = 1219.2   # along y-axis
extrude_distance = 12.7  # along z-axis

# Build the plate centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
