import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0002\neg_02\iter_01\generated.step"

# Design Plan: extruded rectangle
# Dimensions: length_u = 193.0 mm (but perturbed to 231.6 mm per perturbation description)
#             width_v = 55.0 mm (from curves: 55.0 mm)
#             extrude_distance = 50.0 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: rectangle in XZ plane (u=X, v=-Z), extrude along Y (w)

# Build the rectangle in the XZ plane (since v_dir = [0,0,-1], u_dir = [1,0,0])
# Rectangle corners in UV space: (0,0), (231.6,0), (231.6,55), (0,55)
# Map to XYZ: U->X, V->-Z (since v_dir = [0,0,-1])
# So: (0,0) -> (0, 0, 0)
#     (231.6,0) -> (231.6, 0, 0)
#     (231.6,55) -> (231.6, 0, -55)
#     (0,55) -> (0, 0, -55)

# Create workplane on XZ plane (normal = Y axis)
wp = cq.Workplane("XZ")

# Draw rectangle using polyline and close
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
cq.exporters.export(result, OUT_STEP_PATH)