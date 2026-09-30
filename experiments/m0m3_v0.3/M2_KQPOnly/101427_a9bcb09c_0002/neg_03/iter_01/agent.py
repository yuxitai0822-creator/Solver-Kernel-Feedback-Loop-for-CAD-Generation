import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0002\neg_03\iter_01\generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion):
# Rectangle: length_u = 193.0 mm, width_v = 55.0 mm
# Extrude distance: 50.0 mm along +w direction
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle lies in the X-Z plane (u-v plane), extruded along Y (w direction)

# Build the rectangle on the XZ plane (cadquery's default is XY, so we need to work on XZ)
# Using Workplane("XZ") gives us a plane with normal in Y direction
wp = cq.Workplane("XZ")

# The rectangle dimensions: 193.0 mm along X (u), 55.0 mm along Z (v)
# But note: v_dir = [0,0,-1], so the rectangle's v dimension is along -Z
# This means the rectangle spans from Z=0 to Z=-55 (or Z=-55 to Z=0)
# The profile curves show start_uv and end_uv:
#   (0,55) -> (0,0) : along v direction (Z axis)
#   (0,0) -> (193,0) : along u direction (X axis)
#   (193,0) -> (193,55) : along v direction
#   (193,55) -> (0,55) : along u direction
# So the rectangle is at v=0 to v=55 in UV space, but v_dir = -Z, so Z = -v
# This means Z goes from 0 to -55
# To keep it simple, we'll create the rectangle centered at the origin
# with width=193 along X and height=55 along Z

# Create the rectangle centered at origin
result = wp.center(0, 0).rect(193.0, 55.0, centered=True).extrude(50.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")