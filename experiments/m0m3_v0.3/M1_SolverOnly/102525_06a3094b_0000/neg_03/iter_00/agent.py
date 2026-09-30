import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SOIC-8 body
# Dimensions: 3.9 mm (u) x 4.9 mm (v) x 1.55 mm (w)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in uv-plane
# Extrude along +w direction

# Build the rectangle profile
# The profile is centered at (0,0) in the uv-plane
# u spans from -1.95 to 1.95 (total 3.9 mm)
# v spans from -2.45 to 2.45 (total 4.9 mm)

# Create workplane on XZ plane (since v_dir = [0,0,-1], the sketch plane is XZ)
# Actually, with u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]:
#   u -> X axis
#   v -> -Z axis (so Z axis is -v)
#   w -> Y axis
# So the sketch plane is XZ (normal = Y = w_dir)

wp = cq.Workplane("XZ")

# Draw centered rectangle: width=3.9 (along X=u), height=4.9 (along Z=-v)
# Since v_dir = [0,0,-1], the v dimension maps to -Z, so height=4.9 along Z
wp = wp.center(0, 0).rect(3.9, 4.9, centered=True)

# Extrude along +w = +Y direction by 1.55 mm
result = wp.extrude(1.55)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0000\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
