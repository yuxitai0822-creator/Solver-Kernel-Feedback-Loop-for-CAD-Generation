import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism (SOP-28 body)
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in UV plane
# Extrude along +w (Y axis) by 3.0 mm

# Build the rectangle profile on the XZ plane (since v_dir is -Z, u_dir is X, w_dir is Y)
# The rectangle spans u: [-5.65, 5.65] and v: [-10.5, 10.5] (since v_dir is -Z, v coordinate maps to -Z)
# We'll work on XY plane and then rotate, or directly on XZ plane

# Using XZ workplane: u -> X, v -> Z (but v_dir is -Z, so we negate Z coordinates)
# Actually simpler: create on XY plane with correct dimensions, then rotate to align with frame

# Create the base rectangle on XY plane (centered)
result = (cq.Workplane("XY")
          .center(0, 0)
          .rect(11.3, 21.0)  # length_u=11.3 along X, width_v=21.0 along Y
          .extrude(3.0))      # extrude along Z (w_dir should be Y, but we'll rotate)

# Rotate to match frame: w_dir=[0,1,0] means extrusion should be along Y
# Current extrusion is along Z, so rotate -90 deg around X axis
result = result.rotate((0,0,0), (1,0,0), -90)

# Now the part is oriented correctly:
# - X axis corresponds to u_dir (length 11.3)
# - Z axis corresponds to v_dir (width 21.0, but v_dir is -Z, so we need to check)
# - Y axis corresponds to w_dir (extrude 3.0)

# The v_dir is [0,0,-1], meaning the width direction is negative Z.
# Our rectangle had width 21.0 along Y before rotation, after rotation it's along Z.
# But we need to ensure the sign matches. The profile coordinates show v from -10.5 to 10.5,
# which is symmetric, so sign doesn't matter for the shape.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0006\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
