import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Washer (2)
# Extruded annulus with outer radius 3.49 mm, inner radius 2.0 mm, thickness 0.36 mm
# The previous script used a perturbed thickness of 0.5399999999999999 mm (from cm conversion)
# This script uses the correct design dimensions: outer_radius=3.49, inner_radius=2.0, extrude_distance=0.36

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\107055_0500fdd1_0027\neg_01\iter_00/generated.step"

# Build the washer: create outer circle, then inner circle, extrude
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer radius
    .circle(2.0)   # inner radius (creates a hole)
    .extrude(0.36) # thickness
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
