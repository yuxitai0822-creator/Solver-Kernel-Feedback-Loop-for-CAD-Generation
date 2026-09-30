import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (washer-like bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# The previous script used 18.0 mm (incorrectly scaled from perturbed cm value)
# We must use the design plan values directly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0012\neg_01\iter_00/generated.step"

# Parameters from design plan (in mm)
outer_radius = 6.0
inner_radius = 4.25
extrude_distance = 12.0

# Build the annulus on the XZ plane (as per previous script's WORKPLANE = 'XZ')
# The normal is [0, 1, 0] which means extrude along Y axis
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
