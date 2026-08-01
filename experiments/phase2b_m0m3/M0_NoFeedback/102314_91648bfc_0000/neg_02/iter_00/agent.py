import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102314_91648bfc_0000\neg_02\iter_00\generated.step"

# Design parameters from the design plan (unit: mm)
# Outer radius: 12.7 mm (from dimensions.outer_radius)
# Inner radius: 7.965948 mm (from dimensions.inner_radius)
# Extrude distance: 101.6 mm (from dimensions.extrude_distance)
# Note: The perturbation description says radius changed from 1.27 to 1.5875,
# but that appears to be a different radius (perhaps in cm). The design plan
# explicitly gives outer_radius=12.7 and inner_radius=7.965948 in mm.
# We follow the design plan dimensions.

outer_radius = 12.7
inner_radius = 7.965948
extrude_height = 101.6

# Build the annulus (washer shape) by extruding a circle and cutting the inner hole
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .extrude(extrude_height)
    .faces("<Z")
    .workplane()
    .hole(inner_radius * 2, extrude_height)
)

# Export to STEP
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
