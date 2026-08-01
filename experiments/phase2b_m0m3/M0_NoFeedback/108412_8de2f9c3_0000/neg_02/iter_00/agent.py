import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The perturbation description indicates the original was 243.84, perturbed to 292.608
# This appears to be a scaling factor applied to the coordinates
# Original coordinates in the design plan: 121.92, -60.96, etc.
# These are half-dimensions: 2438.4/2 = 1219.2, 1219.2/2 = 609.6
# But the design plan shows 121.92 and 60.96 - these are in cm, converted to mm = 1219.2 and 609.6
# The perturbation scales these by 292.608/243.84 = 1.2
# So perturbed half-dimensions: 1219.2 * 1.2 = 1463.04, 609.6 * 1.2 = 731.52
# But the previous script used 1463.04 and 609.6 - inconsistent scaling
# Let's use the design plan values directly: 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm
# Extrude: 12.7 mm

# Build the rectangle centered at origin
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2, centered=True)
    .extrude(12.7)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108412_8de2f9c3_0000\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)