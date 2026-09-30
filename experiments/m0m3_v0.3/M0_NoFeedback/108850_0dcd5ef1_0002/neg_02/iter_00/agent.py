import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle: 171.45 x 38.1 x 6.35 mm
# The perturbation changes the length from 171.45 to 20.574 (but the design plan says 171.45)
# We follow the design plan exactly: rectangle 171.45 x 38.1, extrude 6.35 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108850_0dcd5ef1_0002\neg_02\iter_00\generated.step"

# Build the part according to the design plan
# The profile is a rectangle with corners at (0,0), (17.145,0), (17.145,3.81), (0,3.81) in UV space
# But the dimensions say length_u=171.45, width_v=38.1
# The UV coordinates in the design plan are scaled by 10 (cm to mm conversion)
# So the actual rectangle is 171.45 x 38.1 mm

# Create a workplane on XY plane (default)
result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1, centered=False)
    .extrude(6.35)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
