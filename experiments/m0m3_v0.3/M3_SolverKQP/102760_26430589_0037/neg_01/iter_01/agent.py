import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
RADIUS = 0.8  # mm (from dimensions.radius)
HEIGHT = 4.0  # mm (from extrude.distance_total.value)

# The design plan specifies:
# - frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# - extrude direction: -w (i.e., negative w direction)
# - The profile is a circle of radius 0.8 in the uv-plane
# - Extrude distance is 4.0 along -w
#
# In CadQuery, we need to align the workplane with the uv-plane.
# The uv-plane normal is w_dir = [0,1,0]. So we use plane with normal (0,1,0).
# The u direction is [1,0,0] and v direction is [0,0,-1].
# We create a workplane with normal (0,1,0) and then rotate to align u and v.
#
# Alternative: Use a custom plane with explicit u and v axes.
# cq.Plane(origin=(0,0,0), xDir=(1,0,0), normal=(0,1,0)) gives:
#   xDir = (1,0,0) = u
#   zDir = normal = (0,1,0) = w
#   yDir = cross(zDir, xDir) = cross((0,1,0),(1,0,0)) = (0,0,-1) = v
# This matches the required frame exactly.

# Build the disk using the correct orientation
workplane = cq.Workplane(cq.Plane(origin=(0,0,0), xDir=(1,0,0), normal=(0,1,0)))
result = (
    workplane
    .circle(RADIUS)
    .extrude(-HEIGHT)  # extrude in -w direction (negative normal)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102760_26430589_0037\neg_01\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)