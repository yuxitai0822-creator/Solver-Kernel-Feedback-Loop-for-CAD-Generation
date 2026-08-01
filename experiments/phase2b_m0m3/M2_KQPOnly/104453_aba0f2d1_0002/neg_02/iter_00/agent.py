import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_02\iter_00/generated.step"

# Build the stadium profile directly using CadQuery's 2D primitives
# The stadium consists of:
# - Left semicircle: center (0,0), radius 5.0, from 90° to 270° (or 0° to 180° in the design plan)
# - Top line: from (0, 5) to (50, 5)
# - Right semicircle: center (50,0), radius 5.0, from 270° to 90° (or 0° to 180° in the design plan)
# - Bottom line: from (50, -5) to (0, -5)

# Note: The design plan specifies radius=5.0 for the arcs, but the perturbation description
# says the radius was changed from 5.0 to 6.25. However, the validation intents expect
# span_u=600.0 and span_v=100.0, which correspond to straight_length=500.0 and radius=50.0
# (after cm->mm conversion: 5cm->50mm). The perturbation is E3_radius with original=5.0,
# perturbed=6.25 (in cm), which becomes 62.5mm. But the validation expects 50mm radius.
# We follow the design plan dimensions: straight_length=500mm, radius=50mm.

# Create the stadium profile using a workplane
wp = cq.Workplane("XY")

# Build the stadium shape:
# Start at the bottom-left corner of the straight section: (0, -50)
# Go right along bottom line to (500, -50)
# Arc up to (500, 50) via center (500, 0) radius 50
# Go left along top line to (0, 50)
# Arc down to (0, -50) via center (0, 0) radius 50

# Using threeArc and sagittaArc or radiusArc for the semicircles
# radiusArc expects start point, end point, and radius (positive for counterclockwise)

# Build the wire manually
wire = (
    cq.Workplane("XY")
    .moveTo(0, -50)
    .lineTo(500, -50)
    .radiusArc((500, 50), 50)  # Arc from (500,-50) to (500,50) with radius 50
    .lineTo(0, 50)
    .radiusArc((0, -50), 50)  # Arc from (0,50) to (0,-50) with radius 50
    .close()
)

# Extrude the wire to create the solid
result = wire.extrude(100.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
