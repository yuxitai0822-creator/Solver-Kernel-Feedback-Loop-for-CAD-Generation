import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle: 171.45 mm x 38.1 mm, extrude 6.35 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from 0 to 171.45, v from 0 to 38.1
# Extrude in +w direction (y-axis) by 6.35 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108850_0dcd5ef1_0002\neg_01\iter_01/generated.step"

# Use the explicit dimensions from the design plan
length_u = 171.45  # mm
width_v = 38.1     # mm
extrude_distance = 6.35  # mm

# Build the rectangle in the XZ plane (since v_dir = [0,0,-1] means v is -Z, u is X)
# The rectangle spans from u=0 to u=171.45, v=0 to v=38.1 in UV space
# In XYZ: u -> X, v -> -Z (since v_dir = [0,0,-1])
# So X from 0 to 171.45, Z from -38.1 to 0

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Draw rectangle: center at (171.45/2, -38.1/2) with size 171.45 x 38.1
# In XZ plane, X is horizontal, Z is vertical
result = wp.moveTo(length_u/2, -width_v/2).rect(length_u, width_v, centered=True).extrude(extrude_distance)

# Export using correct exporters module
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")