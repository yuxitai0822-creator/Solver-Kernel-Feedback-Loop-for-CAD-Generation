import cadquery as cq
from cadquery import exporters
import math

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm, extrude distance 6.8707 mm
# The perturbation changes extrude depth from 0.68707 cm to 1.030605 cm = 10.30605 mm
# But the design plan says 6.8707 mm - we follow the design plan exactly

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0002\neg_01\iter_01\generated.step"

# Parameters from design plan
radius = 4.87045  # mm
extrude_distance = 6.8707  # mm (from design plan, not perturbed value)

# Build the part
# The profile is a circle in the XY plane, extruded along Z
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
