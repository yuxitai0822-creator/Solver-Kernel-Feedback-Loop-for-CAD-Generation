import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0002\neg_02\iter_01/generated.step"

# The design plan specifies:
# - straight_length = 500.0 mm (after cm->mm conversion: 50cm -> 500mm)
# - radius = 50.0 mm (after cm->mm conversion: 5cm -> 50mm)
# - extrude distance = 100.0 mm
# The validation intents expect:
# - span_u = 600.0 mm (500 + 2*50)
# - span_v = 100.0 mm (2*50)
# - span_w = 100.0 mm
#
# The perturbation description says radius changed from 5.0 to 6.25 (cm),
# which would be 62.5mm. But the validation intents expect 50mm radius.
# We follow the design plan dimensions: straight_length=500mm, radius=50mm.

# Build the stadium profile using a workplane
# Start at bottom-left corner of the straight section: (0, -50)
# Go right along bottom line to (500, -50)
# Arc up to (500, 50) via center (500, 0) radius 50
# Go left along top line to (0, 50)
# Arc down to (0, -50) via center (0, 0) radius 50

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