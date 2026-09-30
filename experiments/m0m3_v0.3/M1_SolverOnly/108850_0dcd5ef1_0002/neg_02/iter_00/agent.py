import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle: 171.45 x 38.1 x 6.35 mm
# The design plan specifies a rectangle in UV space:
#   u: 0 to 17.145 (but note: unit conversion cm->mm, so 17.145 cm = 171.45 mm)
#   v: 0 to 3.81 (3.81 cm = 38.1 mm)
# Extrude distance: 6.35 mm in +w direction
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle lies in the XZ plane (since u and v span X and Z)
# and extrudes along Y (w direction).

# Build the rectangle in the XZ plane
# The rectangle corners in UV: (0,0), (171.45,0), (171.45,38.1), (0,38.1)
# In XYZ: u->X, v->-Z, so:
#   (0,0) -> (0, 0, 0)
#   (171.45,0) -> (171.45, 0, 0)
#   (171.45,38.1) -> (171.45, 0, -38.1)
#   (0,38.1) -> (0, 0, -38.1)

# Create workplane on XZ plane (normal = Y)
wp = cq.Workplane("XZ")

# Draw rectangle centered at (171.45/2, -38.1/2) in XZ plane
# Width along X = 171.45, Height along Z = 38.1
result = wp.center(171.45/2, -38.1/2).rect(171.45, 38.1, centered=True).extrude(6.35)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108850_0dcd5ef1_0002\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)