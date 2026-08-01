import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SOP-28 rectangular prism
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in UV plane
# UV coordinates: u in [-0.565, 0.565], v in [-1.05, 1.05]
# After scaling: u*10 -> [-5.65, 5.65], v*10 -> [-10.5, 10.5]
# But the design plan says length_u=11.3, width_v=21.0, so the rectangle is 11.3 x 21.0
# The profile curves show u range [-0.565, 0.565] and v range [-1.05, 1.05]
# These are in UV space, but the actual dimensions are 11.3 x 21.0
# So the scaling factor is 10: u*10 = x, v*10 = y
# The extrude is along w_dir = [0,1,0] for 3.0 mm

# Build the rectangle on the XZ plane (since v_dir = [0,0,-1], w_dir = [0,1,0])
# Actually, let's use the standard approach: workplane XZ, draw rectangle, extrude along Y

# Rectangle dimensions
length_u = 11.3  # along x
width_v = 21.0   # along z (since v_dir = [0,0,-1])
extrude_dist = 3.0  # along y (w_dir = [0,1,0])

# Create workplane on XZ (front plane)
wp = cq.Workplane("XZ")

# Draw centered rectangle: length_u along X, width_v along Z
# Note: v_dir = [0,0,-1] means the v axis points in -Z direction
# But the rectangle is symmetric, so centered works fine
result = wp.center(0, 0).rect(length_u, width_v).extrude(extrude_dist)

# The result is a rectangular prism centered at origin
# Dimensions: 11.3 x 3.0 x 21.0 (X x Y x Z)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0006\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)