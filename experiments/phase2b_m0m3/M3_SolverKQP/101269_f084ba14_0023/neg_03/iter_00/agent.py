import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u = 95.25 mm, width_v = 571.5 mm, extrude_distance = 19.05 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# Profile rectangle in UV plane: u from 0 to 9.525, v from 0 to 57.15
# Note: The design plan's profile coordinates are in UV space, but the dimensions
# indicate length_u = 95.25 and width_v = 571.5. The profile coordinates appear
# to be scaled by 0.1 (9.525 = 95.25/10, 57.15 = 571.5/10). We'll use the
# explicit dimensions from the design plan.

# Build the rectangle in the XY plane (default workplane)
# Then rotate to match the frame orientation

# Step 1: Create the base rectangle in XY plane
# Rectangle dimensions: 95.25 x 571.5
length_u = 95.25
width_v = 571.5
extrude_dist = 19.05

# Create workplane and draw rectangle centered at origin
result = (cq.Workplane("XY")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_dist))

# The design plan specifies:
# u_dir = [1,0,0] (X axis)
# v_dir = [0,0,-1] (negative Z axis)
# w_dir = [0,1,0] (Y axis)
# 
# Our current result has:
# - rectangle in XY plane (u along X, v along Y)
# - extrude along Z (w along Z)
# 
# We need to rotate so that:
# - u (original X) stays X
# - v (original Y) becomes -Z
# - w (original Z) becomes Y
# 
# This is a rotation: X->X, Y->-Z, Z->Y
# Rotation matrix: [[1,0,0],[0,0,-1],[0,1,0]]
# This is a 90-degree rotation about X axis

result = result.rotate((0,0,0), (1,0,0), 90)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101269_f084ba14_0023\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)