import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0002\neg_02\iter_00\generated.step"

# Design Plan: extruded rectangle
# Dimensions: length_u = 193.0 mm (but perturbed to 231.6 mm per perturbation description)
#             width_v = 55.0 mm (from curves: 55.0 mm)
#             extrude_distance = 50.0 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: rectangle in XZ plane (u=X, v=-Z), extrude along Y (w)

# Perturbation: original length_u = 193.0, perturbed to 231.6
# The curves in the design plan show: start_uv = (0,55), end_uv = (193,0) etc.
# But the perturbation says to use 231.6 instead of 193.0
# However, the curves in the plan show 193.0, so we use the perturbed value 231.6

# Build the rectangle in the XZ plane (since v_dir = [0,0,-1], u_dir = [1,0,0])
# Rectangle corners in UV space: (0,0), (231.6,0), (231.6,55), (0,55)
# Map to XYZ: U->X, V->-Z (since v_dir = [0,0,-1])
# So: (0,0) -> (0, 0, 0)
#     (231.6,0) -> (231.6, 0, 0)
#     (231.6,55) -> (231.6, 0, -55)
#     (0,55) -> (0, 0, -55)

# Create workplane on XZ plane (normal = Y axis)
wp = cq.Workplane("XZ")

# Draw rectangle centered at (231.6/2, -55/2) with width=231.6, height=55
# But we need to be careful: the rectangle should be positioned correctly
# Using the corner coordinates directly via polyline

# Start at (0, 0) in XZ plane (which is (0,0) in workplane coords)
# Then go to (231.6, 0), then (231.6, -55), then (0, -55), then close

result = (
    wp
    .moveTo(0, 0)
    .lineTo(231.6, 0)
    .lineTo(231.6, -55)
    .lineTo(0, -55)
    .close()
    .extrude(50.0)  # extrude along Y (positive direction)
)

# Export
importers.export(result, OUT_STEP_PATH)
