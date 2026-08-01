import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107055_0500fdd1_0027\neg_02\iter_00/generated.step"

# Design parameters from the design plan
# Outer radius: 3.49 mm (from dimensions section, not the perturbed radius in LOOPS)
# Inner radius: 2.0 mm
# Extrude distance: 0.36 mm
outer_radius = 3.49
inner_radius = 2.0
extrude_distance = 0.36

# Build the washer using cadquery
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .circle(outer_radius)  # Outer circle
    .circle(inner_radius)  # Inner circle (creates a hole)
    .extrude(extrude_distance)  # Extrude to create the washer
)

# Export the result
exporters.export(result, OUT_STEP_PATH)
