import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0006\neg_02\iter_00\generated.step"

# Design Plan: Drone Leg - square strut
# Rectangle profile: 19.0mm x 19.0mm (in UV plane)
# Extrude 130.0mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center at origin in UV space, then extrude along +W

# Build the rectangle profile on the XZ plane (since V is [0,0,-1], W is [0,1,0])
# The rectangle dimensions: length_u=19.0, width_v=19.0
# Center the rectangle at origin

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(19.0, 19.0, centered=True)
    .extrude(130.0)
)

exporters.export(result, OUT_STEP_PATH)
