import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102314_91648bfc_0000\neg_01\iter_00\generated.step"

# Design parameters from the design plan (in mm)
# Outer radius: 12.7 mm, Inner radius: 7.965948 mm, Extrude distance: 101.6 mm
outer_radius = 12.7
inner_radius = 7.965948
extrude_distance = 101.6

# Build the annulus (washer shape) using cadquery
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .circle(outer_radius)  # outer circle
    .circle(inner_radius)  # inner circle (creates a hole)
    .extrude(extrude_distance)  # extrude along +Z
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
