import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle: 171.45 mm x 38.1 mm, extruded 6.35 mm
# The profile is a rectangle with corners at (0,0), (171.45,0), (171.45,38.1), (0,38.1)
# Note: The design plan shows u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means the sketch is in the XZ plane, extruded along Y

# Build the rectangle on the XZ plane
result = (
    cq.Workplane("XZ")
    .center(171.45/2, -38.1/2)  # center the rectangle at origin
    .rect(171.45, 38.1)
    .extrude(6.35)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108850_0dcd5ef1_0002\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)