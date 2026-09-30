import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle plate
# Dimensions: length_u = 171.45 mm, width_v = 38.1 mm, extrude_distance = 6.35 mm
# Profile rectangle in UV space: u in [0, 17.145], v in [0, 3.81] (note: values are in cm originally, converted to mm by x10)
# After unit conversion: u in [0, 171.45], v in [0, 38.1]
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in XZ plane, extruded along Y direction

# Build the rectangle profile on XZ plane
# Rectangle corners in UV: (0,0), (171.45,0), (171.45,38.1), (0,38.1)
# Map to XYZ: u->X, v->-Z, so:
# (0,0) -> (0, 0, 0)
# (171.45,0) -> (171.45, 0, 0)
# (171.45,38.1) -> (171.45, 0, -38.1)
# (0,38.1) -> (0, 0, -38.1)

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Create rectangle centered at (85.725, -19.05) with width 171.45 and height 38.1
# Using centered=True for simplicity
result = wp.center(85.725, -19.05).rect(171.45, 38.1, centered=True).extrude(6.35)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108850_0dcd5ef1_0002\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)