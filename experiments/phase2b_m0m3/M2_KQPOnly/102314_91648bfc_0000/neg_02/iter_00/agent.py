import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102314_91648bfc_0000\neg_02\iter_00\generated.step"

# Design parameters from the design plan (unit: mm)
# Outer radius: 12.7 mm (from dimensions.outer_radius)
# Inner radius: 7.965948 mm (from dimensions.inner_radius)
# Extrude distance: 101.6 mm (from dimensions.extrude_distance)
# Note: The perturbation description says radius changed from 1.27 to 1.5875,
# but the design plan clearly states outer_radius=12.7 and inner_radius=7.965948.
# The perturbation likely refers to a different scale or is a comment.
# We follow the explicit dimensions in the design plan.

outer_radius = 12.7
inner_radius = 7.965948
extrude_height = 101.6

# Build the part: extrude an annulus (outer circle minus inner circle)
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_height)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
