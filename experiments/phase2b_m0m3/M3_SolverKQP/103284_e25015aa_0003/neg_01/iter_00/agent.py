import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0003\neg_01\iter_00/generated.step"

# Design Plan parameters (from solid_bodies[0])
# Profile: circle, center_uv = [1.6994660913961006, 1.7998556732836484], radius = 2.54
# Extrude: one_side, +w, distance_total = 8.89
# Dimensions: radius = 25.4, center_uv = [16.994661, 17.998557]
# Note: The profile center_uv and radius appear to be in a different scale than dimensions.
# The dimensions section says radius=25.4, center_uv=[16.994661, 17.998557].
# The profile section says radius=2.54, center_uv=[1.6994660913961006, 1.7998556732836484].
# The compiler notes say unit_conversion_applied: cm_to_mm (x10).
# The profile values are likely in cm (since 2.54 cm = 25.4 mm, 1.699... cm ≈ 16.99 mm).
# So we use the dimension values (in mm): radius=25.4, center=(16.994661, 17.998557), extrude=8.89.

# Build the part
result = (
    cq.Workplane("XY")
    .moveTo(16.994661, 17.998557)
    .circle(25.4)
    .extrude(8.89)
)

# Export STEP
exporters.export(result, OUT_STEP_PATH)
