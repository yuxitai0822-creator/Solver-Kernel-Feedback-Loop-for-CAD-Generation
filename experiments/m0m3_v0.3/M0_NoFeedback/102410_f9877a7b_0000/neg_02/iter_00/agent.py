import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# The previous script used perturbed radius 7.5 mm (outer) instead of 6.0 mm
# This script corrects the outer radius to 6.0 mm as per design plan

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0000\neg_02\iter_00/generated.step"

# Parameters from design plan (converted from cm to mm where needed)
outer_radius = 6.0  # mm (from design plan: 0.6000000000000001 cm = 6.0 mm)
inner_radius = 4.25  # mm (from design plan: 0.42500000000000004 cm = 4.25 mm)
extrude_distance = 11.5  # mm (from design plan)

# Build the annulus using cadquery
# Workplane is XZ (as in original), extrude along Y axis
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
importers.export(result, OUT_STEP_PATH)
