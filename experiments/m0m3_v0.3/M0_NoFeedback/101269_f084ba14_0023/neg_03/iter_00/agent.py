import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101269_f084ba14_0023\neg_03\iter_00\generated.step"

# Design Plan dimensions (in mm):
# Rectangle profile: u (x) = 95.25, v (z) = 571.5 (perturbed from 57.15 to 45.72? No, the perturbation description says 57.15 -> 45.72 but that seems to be a different dimension; the design plan says width_v = 571.5 which is 10x 57.15, so the perturbation likely affected the v-span. Let's use the design plan values: 95.25 x 571.5)
# Extrude distance (w direction, y axis): 19.05

# The frame has:
# u_dir = [1,0,0] (x-axis)
# v_dir = [0,0,-1] (negative z-axis)
# w_dir = [0,1,0] (y-axis)
# So the rectangle is in the XZ plane, extruded along Y.

# Create the rectangle profile on the XZ plane
# The rectangle spans from u=0 to u=95.25, v=0 to v=571.5 (in UV coordinates)
# In world coordinates: u=x, v=-z (since v_dir = [0,0,-1])
# So x from 0 to 95.25, z from -571.5 to 0

# Build the part
result = (
    cq.Workplane("XZ")
    .center(95.25/2, -571.5/2)  # center the rectangle
    .rect(95.25, 571.5)
    .extrude(19.05)  # extrude along Y (positive w direction)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
