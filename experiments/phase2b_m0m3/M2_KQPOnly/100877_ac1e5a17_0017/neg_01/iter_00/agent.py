import cadquery as cq
from cadquery import exporters

# Design Plan: flat rectangular plate 254.0 x 190.5 mm, extruded 3.175 mm
# The previous script used a perturbed extrusion depth of 4.7625 mm (0.47625 cm).
# This script corrects to the design plan value: 3.175 mm.

# Dimensions from design plan (in mm)
LENGTH_U = 254.0   # along x
WIDTH_V = 190.5    # along y
THICKNESS = 3.175  # along z

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0017\neg_01\iter_00/generated.step"

# Build the plate centered on the XY plane, extruded in +Z
result = (
    cq.Workplane("XY")
    .rect(LENGTH_U, WIDTH_V, centered=True)
    .extrude(THICKNESS)
)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
