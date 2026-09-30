import cadquery as cq
from cadquery import exporters
import math

# Constants from design plan
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0002\neg_01\iter_01\generated.step"

# Dimensions from design plan (in mm, converted from cm)
# The design plan specifies:
# - u_dir = [0, 0, -1] (negative Z)
# - v_dir = [0, 1, 0] (positive Y)
# - w_dir = [1, 0, 0] (positive X)
# - Extrude direction: -w = [-1, 0, 0] (negative X)
# - Extrude distance: 1120.0 mm

# The UV coordinates are given in the design plan:
# Outer rectangle: u from -6.12 to -1.88, v from 10.88 to 15.12
# Inner rectangle: u from -6.0 to -2.0, v from 11.0 to 15.0

# The span along u should be 42.4 mm, along v should be 42.4 mm
# This means the UV coordinates are in cm, not mm!
# -6.12 to -1.88 = 4.24 cm = 42.4 mm
# 10.88 to 15.12 = 4.24 cm = 42.4 mm

# So we need to convert UV coordinates from cm to mm by multiplying by 10
# Outer rectangle in UV (mm): u from -61.2 to -18.8, v from 108.8 to 151.2
# Inner rectangle in UV (mm): u from -60.0 to -20.0, v from 110.0 to 150.0

# Convert UV to YZ coordinates: u->Z, v->Y
# u_dir = [0, 0, -1] means u axis points in negative Z
# So u coordinate maps to -Z
# u=-61.2 -> Z = 61.2, u=-18.8 -> Z = 18.8
# u=-60.0 -> Z = 60.0, u=-20.0 -> Z = 20.0

# Outer rectangle in YZ plane (mm):
#   Y: 108.8 to 151.2
#   Z: 18.8 to 61.2

# Inner rectangle in YZ plane (mm):
#   Y: 110.0 to 150.0
#   Z: 20.0 to 60.0

# Extrude direction: -w = -[1, 0, 0] = [-1, 0, 0] (negative X)
# Extrude distance: 1120.0 mm

# Build the outer profile
result = (cq.Workplane("YZ")
    .center(0, 0)
    .moveTo(18.8, 108.8)  # Start at outer corner (Z=18.8, Y=108.8)
    .lineTo(18.8, 151.2)   # Top edge
    .lineTo(61.2, 151.2)   # Right edge
    .lineTo(61.2, 108.8)   # Bottom edge
    .close()               # Back to start
    .extrude(1120.0)       # Extrude in positive X direction
)

# Build the inner profile for cutting
inner = (cq.Workplane("YZ")
    .center(0, 0)
    .moveTo(20.0, 110.0)  # Start at inner corner (Z=20.0, Y=110.0)
    .lineTo(20.0, 150.0)   # Top edge
    .lineTo(60.0, 150.0)   # Right edge
    .lineTo(60.0, 110.0)   # Bottom edge
    .close()               # Back to start
    .extrude(1120.0)       # Same extrusion distance
)

# Subtract inner from outer to create the hollow frame
result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
