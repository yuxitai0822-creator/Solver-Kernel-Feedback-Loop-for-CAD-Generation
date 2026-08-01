import cadquery as cq
from cadquery import exporters
import math

# Design Plan: flat rectangular plate
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The perturbation description says E2_extrude_depth original=1.27, perturbed=1.905 (cm)
# But the design plan explicitly states 12.7 mm (which is 1.27 cm).
# The previous script used 19.05 mm (1.905 cm) which is the perturbed value.
# Since this is iteration 0 and we must follow the design plan, we use 12.7 mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108412_8de2f9c3_0000\neg_01\iter_00/generated.step"

# Rectangle dimensions from design plan
length_u = 2438.4  # mm (along x-axis)
width_v = 1219.2   # mm (along y-axis)
extrude_distance = 12.7  # mm (along z-axis)

# Create the rectangular plate centered at origin
# The profile coordinates in the design plan span from -121.92 to 121.92 in u and -60.96 to 60.96 in v
# But the dimensions say length_u=2438.4 and width_v=1219.2
# The coordinates in the design plan appear to be in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm)
# So the actual rectangle is 2438.4 mm x 1219.2 mm

# Build the plate
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
