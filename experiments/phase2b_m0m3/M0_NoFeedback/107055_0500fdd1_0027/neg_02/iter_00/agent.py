import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Washer (2) - extruded annulus
# Outer radius: 3.49 mm (from dimensions.profiles[0].outer_radius)
# Inner radius: 2.0 mm (from dimensions.profiles[0].inner_radius)
# Extrude distance: 0.36 mm (from dimensions.extrude_distance)
# Note: The perturbation description mentions E3_radius with original=0.349, perturbed=0.43625
# but the design plan dimensions clearly state outer_radius=3.49, inner_radius=2.0
# We follow the design plan dimensions as the authoritative source.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107055_0500fdd1_0027\neg_02\iter_00\generated.step"

# Create the washer by extruding an annulus (outer circle minus inner circle)
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer radius
    .circle(2.0)   # inner radius (creates a hole)
    .extrude(0.36) # extrude distance
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
