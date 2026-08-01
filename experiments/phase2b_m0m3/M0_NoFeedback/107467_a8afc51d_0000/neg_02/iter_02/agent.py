import cadquery as cq
from cadquery import exporters

# Design Plan: single disk (extruded circle)
# - Circle radius: 3.0 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance: 14.0 mm (from dimensions.extrude_distance.value)
# - The perturbed radius 0.375 is for the sketch profile radius (the circle radius in the profile curves)
#   but the design plan says the profile radius is 3.0 mm. The perturbation description says
#   original=0.30000000000000004, perturbed=0.37500000000000006. This is the radius of the circle
#   in the profile curves (the sketch circle). The design plan's dimensions.profiles[0].radius.value
#   is 3.0, which is the overall part radius. The profile curve radius is 0.375 (perturbed).
#   Wait: The design plan says radius=0.30000000000000004 in the curves, and dimensions.profiles[0].radius.value=3.0.
#   This is confusing. Let's re-read: The design plan has:
#     profiles[0].rings[0].curves[0].radius = 0.30000000000000004
#     dimensions.profiles[0].radius.value = 3.0
#   The perturbation says original=0.30000000000000004, perturbed=0.37500000000000006.
#   So the sketch circle radius is 0.375 mm (perturbed). The extrude distance is 14.0 mm.
#   The part should be a cylinder with radius 0.375 mm and height 14.0 mm.
#   But the validation intents expect span_u=6.0, span_v=6.0, which would be for radius 3.0.
#   This is a negative perturbation: the radius is changed from 3.0 to 0.375.
#   The design plan's dimensions.profiles[0].radius.value=3.0 is the original, but the perturbation
#   changes the curve radius to 0.375. So we use the perturbed value.
#   The validation intents will fail (expected 6.0 span, but actual will be 0.75), but that's
#   the point of negative perturbation.

# Build the part
result = (
    cq.Workplane("XY")
    .circle(0.375)  # perturbed radius
    .extrude(14.0)   # extrude distance
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0000\neg_02\iter_02\generated.step"
exporters.export(result, OUT_STEP_PATH)