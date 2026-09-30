import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Washer (2)
# Outer radius = 3.49 mm, Inner radius = 2.0 mm, Thickness = 0.36 mm
# Note: The perturbation description mentions E3_radius with original=0.349 and perturbed=0.43625
# but the design plan dimensions clearly state outer_radius=3.49 and inner_radius=2.0
# We follow the design plan exactly as specified.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\107055_0500fdd1_0027\neg_02\iter_00/generated.step"

# Create the washer using the design plan dimensions
# Outer circle radius = 3.49 mm
# Inner circle radius = 2.0 mm
# Extrude distance = 0.36 mm

# Build the outer circle
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer radius
    .circle(2.0)   # inner radius (creates a hole)
    .extrude(0.36) # thickness
)

# Export the result
exporters.export(result, OUT_STEP_PATH)
