import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
# Rectangle dimensions: length_u = 11.3 mm, width_v = 21.0 mm
# Extrude distance: 3.0 mm (one side, +w direction)
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle is in the XZ plane, extruded along Y

# Create the rectangle in the XZ plane
# The rectangle is centered at the origin with dimensions 11.3 x 21.0
# In the frame: u (X) = 11.3, v (Z) = 21.0 (but v_dir is [0,0,-1], so we negate)
# Actually, the profile coordinates are in UV space:
#   u ranges from -0.565 to 0.565 (half of 11.3)
#   v ranges from -1.05 to 1.05 (half of 21.0)
# The frame maps: u -> X, v -> -Z
# So in world coordinates:
#   X = u, Z = -v
#   The rectangle corners in XZ: 
#     (0.565, 1.05), (0.565, -1.05), (-0.565, -1.05), (-0.565, 1.05)
#   But v is negated, so Z = -v:
#     (0.565, -1.05), (0.565, 1.05), (-0.565, 1.05), (-0.565, -1.05)
# This is just a rectangle centered at origin with width 11.3 along X and height 21.0 along Z

# Build the workplane on XZ plane (normal = Y)
wp = cq.Workplane("XZ")

# Create the rectangle centered at origin
# rect(width, height, centered=True) creates a rectangle centered at current point
# width along X, height along Z (since workplane is XZ)
wp = wp.center(0, 0).rect(11.3, 21.0, centered=True)

# Extrude along Y (positive direction, which is +w in the frame)
# The design plan says extrude distance = 3.0 mm, one side, +w direction
result = wp.extrude(3.0)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0006\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
