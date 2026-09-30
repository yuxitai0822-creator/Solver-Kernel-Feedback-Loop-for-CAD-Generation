import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, Total extrusion = 10.0 mm (symmetric)
# The previous script used perturbed radius 21.875 (outer) which is wrong.
# We correct to the design plan values.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106323_77f22d29_0004\neg_02\iter_00/generated.step"

# Parameters from design plan (unit: mm)
outer_radius = 17.5
inner_radius = 12.5
total_extrude = 10.0  # symmetric, so half on each side

# Build the annulus
# Start with outer circle, then cut inner circle
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(total_extrude / 2, both=True)  # symmetric extrusion
)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
