import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101269_f084ba14_0023\neg_02\iter_01\generated.step"

# Design Plan: extruded rectangle
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The design plan dimensions say length_u=95.25, width_v=571.5, extrude_distance=19.05
# The perturbation changes the u-dimension from 9.525 to 11.43 (but this is a scaling factor)
# Looking at the curves: u ranges from 0 to 9.525, v ranges from 0 to 57.15
# The dimensions say length_u=95.25, width_v=571.5
# 95.25 / 9.525 = 10, 571.5 / 57.15 = 10
# So the actual rectangle in UV space is u from 0 to 95.25, v from 0 to 571.5
# The perturbation changes the original 9.525 to 11.43, which means the scaling factor changes
# But the dimensions are the ground truth: length_u=95.25, width_v=571.5
# The perturbation description says "original=9.525; perturbed=11.43"
# This likely means the u-dimension of the rectangle should be 11.43 * 10 = 114.3?
# Or the perturbation is applied to the curve coordinates directly?
# Let me re-read: "operator=E1_envelope; original=9.525000000000013; perturbed=11.430000000000016"
# This changes the u-coordinate from 9.525 to 11.43 in the curves
# So the rectangle in UV space becomes u from 0 to 11.43, v from 0 to 57.15
# But the dimensions say length_u=95.25, width_v=571.5
# The kernel feedback says expected u=95.25, actual u=11.43
# So the dimensions are the target, and the perturbation should make the rectangle match the dimensions
# Wait, the perturbation is supposed to be a negative CAD operation
# The original script had u from 0 to 9.525, v from 0 to 57.15
# The perturbation changes 9.525 to 11.43
# But the dimensions say length_u=95.25, width_v=571.5
# So the correct rectangle should be u from 0 to 95.25, v from 0 to 571.5
# The perturbation is applied to the curve coordinates, but the dimensions are the ground truth
# So I should use the dimensions: length_u=95.25, width_v=571.5
# The perturbation changes the curve coordinates, but the dimensions override
# Actually, looking at the previous iteration feedback:
#   expected u=95.25, actual u=11.43
#   expected v=571.5, actual v=57.15
# So the script produced a rectangle of size 11.43 x 57.15, but the expected is 95.25 x 571.5
# The perturbation changes 9.525 to 11.43, but the dimensions say 95.25
# This is confusing. Let me look at the original design plan more carefully.
# The curves show u from 0 to 9.525, v from 0 to 57.15
# The dimensions say length_u=95.25, width_v=571.5
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)"
# So the original was in cm, converted to mm by multiplying by 10
# 9.525 cm = 95.25 mm, 57.15 cm = 571.5 mm
# So the curves are in cm, and the dimensions are in mm after conversion
# The perturbation changes 9.525 to 11.43 (in cm)
# So the perturbed rectangle in mm is: u from 0 to 114.3, v from 0 to 571.5
# But the dimensions say length_u=95.25, which is the original unperturbed value
# The perturbation is supposed to be applied, so the rectangle should be 114.3 x 571.5
# But the kernel expects 95.25 x 571.5
# This is a contradiction. Let me re-read the perturbation description.
# "operator=E1_envelope; original=9.525000000000013; perturbed=11.430000000000016 (see TODO: negative CAD code not yet wired)"
# The TODO says "negative CAD code not yet wired"
# So the perturbation is not actually applied yet? Or it's a note for future?
# The previous iteration used 11.43 and 57.15 (the perturbed values)
# But the kernel expected 95.25 and 571.5
# So the dimensions in the design plan are the target, and the perturbation is a modification
# The perturbation changes the u-dimension from 9.525 to 11.43 (in cm)
# But the dimensions say length_u=95.25 (in mm)
# 9.525 cm = 95.25 mm, 11.43 cm = 114.3 mm
# So the perturbed rectangle should be 114.3 x 571.5
# But the kernel expects 95.25 x 571.5
# This means the perturbation is not applied? Or the kernel is checking the original dimensions?
# Let me look at the validation_intents:
#   q_span_u: expected 95.25, tolerance 0.01
#   q_span_v: expected 571.5, tolerance 0.01
#   q_span_w: expected 19.05, tolerance 0.01
# These are the target dimensions
# The perturbation changes the u-dimension, but the validation expects the original
# This is a negative CAD scenario: the perturbation should make the part fail validation
# So the perturbed rectangle should be 114.3 x 571.5, which will fail the u-span check
# But the previous iteration used 11.43 x 57.15 (which is 10x smaller)
# The kernel expected 95.25 x 571.5, so it failed
# The correct perturbed rectangle should be 114.3 x 571.5
# Let me verify: 11.43 cm = 114.3 mm, 57.15 cm = 571.5 mm
# So the rectangle in UV space (in mm) is u from 0 to 114.3, v from 0 to 571.5
# In world coordinates:
#   u_dir = [1, 0, 0] -> x axis
#   v_dir = [0, 0, -1] -> -z axis
#   w_dir = [0, 1, 0] -> y axis
# So the rectangle in world: x from 0 to 114.3, z from -571.5 to 0
# Extrude in +y direction by 19.05 mm

# Build the rectangle using a polyline in the XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .lineTo(114.3, 0)
    .lineTo(114.3, -571.5)
    .lineTo(0, -571.5)
    .close()
    .extrude(19.05)
)

exporters.export(result, OUT_STEP_PATH)