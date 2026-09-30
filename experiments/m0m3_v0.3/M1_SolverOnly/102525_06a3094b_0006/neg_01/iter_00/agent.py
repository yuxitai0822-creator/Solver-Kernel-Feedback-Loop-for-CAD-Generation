import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SOP-28 rectangular prism
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in UV plane

# Build the rectangle profile in the UV plane (XZ plane in CadQuery)
# u -> X axis, v -> Z axis (since v_dir=[0,0,-1], we use positive Z for simplicity)
# w -> Y axis (extrusion direction)

# Create workplane on XZ plane (Y normal)
wp = cq.Workplane("XZ")

# Rectangle dimensions
length_u = 11.3  # mm (along X)
width_v = 21.0   # mm (along Z)
extrude_dist = 3.0  # mm (along Y)

# Create centered rectangle on XZ plane
# rect(width, height) where width is along X, height along Z
result = wp.center(0, 0).rect(length_u, width_v, centered=True).extrude(extrude_dist)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0006\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
