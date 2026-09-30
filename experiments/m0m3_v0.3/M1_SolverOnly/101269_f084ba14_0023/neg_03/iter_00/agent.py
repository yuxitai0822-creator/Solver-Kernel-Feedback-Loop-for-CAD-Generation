import cadquery as cq
import math
from pathlib import Path

OUT_STEP_PATH = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101269_f084ba14_0023\neg_03\iter_00\generated.step")

# Design Plan dimensions (all in mm)
# Rectangle profile in UV frame:
#   U direction: [1,0,0] (X axis)
#   V direction: [0,0,-1] (negative Z axis)
#   W direction: [0,1,0] (Y axis)
# Profile: rectangle with corners at (0,0), (0,57.15), (9.525,57.15), (9.525,0)
#   But note: the curves are given in UV coordinates, and the rectangle spans:
#     U: 0 to 9.525  (length_u = 95.25? Wait, the curves show start/end UV points)
#     V: 0 to 57.15
#   However, the dimensions say length_u = 95.25, width_v = 571.5
#   This is a scaling factor of 10x. The curves are in cm? The compiler notes say cm_to_mm (x10).
#   So the actual UV coordinates in mm are: U: 0 to 95.25, V: 0 to 571.5
#   But the curves show 9.525 and 57.15 — those are in cm. Multiply by 10 to get mm.
#   Let's use the explicit dimensions: length_u = 95.25 mm, width_v = 571.5 mm
#   Extrude distance = 19.05 mm along W (Y axis)

# Build the rectangle in the XZ plane (since V is -Z, U is X, W is Y)
# Workplane: XZ (front plane), then we'll position the rectangle

# Rectangle dimensions
length_u = 95.25  # along X
width_v = 571.5   # along Z (but V direction is [0,0,-1], so positive V goes negative Z)
extrude_dist = 19.05  # along Y (W direction)

# Create the rectangle centered at origin, then extrude
result = (
    cq.Workplane("XZ")
    .center(length_u / 2, -width_v / 2)  # center the rectangle; V positive goes -Z, so we offset accordingly
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export
cq.exporters.export(result, str(OUT_STEP_PATH))
