import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Outer rectangle: from UV coordinates (-6.12, 10.88) to (-1.88, 15.12)
# Inner rectangle: from UV coordinates (-6.0, 11.0) to (-2.0, 15.0)
# Extrude distance: 1120.0 mm (original was 1680.0, but design plan says 1120.0)
# Frame axes: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# This means the profile is in the YZ plane (u,v) and extrudes along X (w)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0002\neg_01\iter_00\generated.step"

# Build the profile in the YZ plane (using Workplane("YZ"))
# The UV coordinates map to YZ coordinates:
#   u -> Z (since u_dir = [0,0,-1], so positive u goes negative Z)
#   v -> Y (since v_dir = [0,1,0])
# We'll work in YZ plane and negate Z to match the u direction

# Outer rectangle corners in UV: (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88)
# Convert to YZ: Y = v, Z = -u
outer_yz = [
    (10.88, 1.88),   # v=10.88, u=-1.88 -> Z=1.88
    (15.12, 1.88),   # v=15.12, u=-1.88 -> Z=1.88
    (15.12, 6.12),   # v=15.12, u=-6.12 -> Z=6.12
    (10.88, 6.12),   # v=10.88, u=-6.12 -> Z=6.12
]

# Inner rectangle corners in UV: (-6.0, 11.0), (-2.0, 11.0), (-6.0, 15.0), (-2.0, 15.0)
# But the inner loop order in the design plan is:
#   (-6.0, 11.0) -> (-2.0, 11.0) -> (-6.0, 15.0) -> (-6.0, 11.0) ???
# Wait, let me re-read the inner curves:
#   curve 0: start=(-6.0, 11.0), end=(-2.0, 11.0)
#   curve 1: start=(-6.0, 15.0), end=(-6.0, 11.0)
#   curve 2: start=(-2.0, 15.0), end=(-6.0, 15.0)
#   curve 3: start=(-2.0, 11.0), end=(-2.0, 15.0)
# This is a rectangle from (-6.0, 11.0) to (-2.0, 15.0) but the order is weird.
# Let me re-order properly: the rectangle corners are (-6.0, 11.0), (-2.0, 11.0), (-2.0, 15.0), (-6.0, 15.0)
inner_yz = [
    (11.0, 6.0),    # v=11.0, u=-6.0 -> Z=6.0
    (11.0, 2.0),    # v=11.0, u=-2.0 -> Z=2.0
    (15.0, 2.0),    # v=15.0, u=-2.0 -> Z=2.0
    (15.0, 6.0),    # v=15.0, u=-6.0 -> Z=6.0
]

# Extrude distance: 1120.0 mm along w_dir = [1,0,0] (positive X)
# The design plan says direction = "-w", so extrude in negative X direction
# But we'll extrude positive X and then check orientation

# Build the outer rectangle
result = (cq.Workplane("YZ")
    .polyline(outer_yz)
    .close()
    .extrude(1120.0)  # extrude along X (positive direction)
)

# Build the inner rectangle as a cutting tool
inner_wire = (cq.Workplane("YZ")
    .polyline(inner_yz)
    .close()
    .extrude(1120.0)
)

# Cut the inner hole
result = result.cut(inner_wire)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
