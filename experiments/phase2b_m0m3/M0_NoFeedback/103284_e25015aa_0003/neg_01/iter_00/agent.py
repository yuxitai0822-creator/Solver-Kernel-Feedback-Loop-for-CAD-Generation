import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\103284_e25015aa_0003\neg_01\iter_00/generated.step"

# Design Plan parameters:
# - Circle center at (16.994660913961006, 17.998556732836484) in UV plane
# - Circle radius = 25.4 mm (from dimensions.radius.value)
# - Extrude distance = 8.89 mm (from extrude.distance_total.value)
# - The profile center_uv is given as [16.994661, 17.998557] which matches
# - The circle in profiles.rings.curves has center_uv [1.6994660913961006, 1.7998556732836484] and radius 2.54
#   BUT the dimensions section says radius=25.4 and center_uv=[16.994661, 17.998557]
#   The compiler note says unit_conversion_applied: cm_to_mm (x10)
#   So the original values were in cm: radius 2.54 cm = 25.4 mm, center (1.699466, 1.799856) cm = (16.99466, 17.99856) mm
#   The dimensions section already has the mm-converted values.
# - Extrude distance: 8.89 mm (from extrude.distance_total.value)
# - The perturbation description says: operator=E2_extrude_depth; original=0.8889999999999999; perturbed=1.3335
#   This is in cm? original 0.889 cm = 8.89 mm, perturbed 1.3335 cm = 13.335 mm
#   The previous script used EXTENT_TOTAL_MM = 13.334999999999999 which matches the perturbed value.
#   But the Design Plan says extrude distance = 8.89 mm (the original, unperturbed value).
#   Since this is iteration 0 and the perturbation description says "TODO: replace with negative CAD code",
#   we should follow the Design Plan which specifies 8.89 mm.

# Build the part:
# 1. Create a workplane on XY
# 2. Draw a circle at (16.99466, 17.99856) with radius 25.4
# 3. Extrude by 8.89 mm in +Z direction

result = (
    cq.Workplane("XY")
    .moveTo(16.994660913961006, 17.998556732836484)
    .circle(25.4)
    .extrude(8.89)
)

exporters.export(result, OUT_STEP_PATH)
