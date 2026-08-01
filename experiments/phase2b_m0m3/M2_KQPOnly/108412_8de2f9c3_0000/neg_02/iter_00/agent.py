import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108412_8de2f9c3_0000\neg_02\iter_00\generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion):
# Rectangle: length_u = 2438.4 mm, width_v = 1219.2 mm
# Extrude distance: 12.7 mm
# The profile coordinates in the design plan are given in UV space:
#   start_uv = [121.92, -60.96] ... end_uv = [121.92, 60.96] etc.
# These are in cm originally? Actually the plan says unit_conversion_applied: cm_to_mm (x10)
# So the UV values are in mm already. But the dimensions say length_u=2438.4, width_v=1219.2.
# The UV coordinates given span from -121.92 to 121.92 in both axes, which is 243.84 mm.
# That's 1/10 of the expected 2438.4 mm. So we need to scale the profile by 10x.
# Alternatively, we can just build the rectangle directly from the dimensions.

# Build the part using the explicit dimensions from the design plan:
length_u = 2438.4  # mm
width_v = 1219.2   # mm
extrude_dist = 12.7  # mm

# Create workplane on XY plane
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_dist)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
