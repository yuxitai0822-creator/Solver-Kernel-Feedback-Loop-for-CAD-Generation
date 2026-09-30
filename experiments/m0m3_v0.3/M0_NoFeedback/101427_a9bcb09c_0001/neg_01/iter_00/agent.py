import cadquery as cq
from cadquery import exporters
import math

# Constants from design plan
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0001\neg_01\iter_00\generated.step"

# Dimensions (in mm, converted from cm)
# Outer rectangle: from curves, min x=-2.5, max x=195.5, min y=-2.5, max y=57.5
# But the design plan says outer_length_u=1980, outer_width_v=600, inner_length_u=1930, inner_width_v=550
# The curves in the design plan are in UV space, not world coordinates
# Let's use the explicit dimensions from the design plan

OUTER_LENGTH = 1980.0  # mm (along u direction)
OUTER_WIDTH = 600.0    # mm (along v direction)
INNER_LENGTH = 1930.0  # mm
INNER_WIDTH = 550.0    # mm
EXTRUDE_DEPTH = 25.0   # mm (from design plan, not the perturbed 37.5)

# Build the frame
result = (
    cq.Workplane("XZ")
    .rect(OUTER_LENGTH, OUTER_WIDTH, centered=True)
    .extrude(EXTRUDE_DEPTH)
)

# Cut inner hole
inner = (
    cq.Workplane("XZ")
    .rect(INNER_LENGTH, INNER_WIDTH, centered=True)
    .extrude(EXTRUDE_DEPTH * 1.5)  # overshoot to ensure clean cut
)

result = result.cut(inner)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
