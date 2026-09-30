import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 12.7 mm, Inner radius = 7.965948 mm, Extrude distance = 101.6 mm
# Note: The previous script used perturbed radius 15.875 (from E3_radius perturbation)
# but the design plan specifies outer radius = 12.7. We follow the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102314_91648bfc_0000\neg_02\iter_00/generated.step"

# Parameters from design plan
outer_radius = 12.7  # mm
inner_radius = 7.965948  # mm
extrude_distance = 101.6  # mm

# Build the annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
