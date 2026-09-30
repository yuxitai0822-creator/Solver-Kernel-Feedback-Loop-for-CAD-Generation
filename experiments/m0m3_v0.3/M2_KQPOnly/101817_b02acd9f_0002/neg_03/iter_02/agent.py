import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0002\neg_03\iter_02\generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (-6.12, 10.88) to (-1.88, 15.12) in UV plane
# Inner rectangle: corners at (-6.0, 11.0) to (-2.0, 15.0) in UV plane
# Extrude direction: -w (which is -x in world frame since w_dir = [1,0,0])
# Extrude distance: 1120.0 mm
# The frame axes: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So UV plane is YZ plane (u=z, v=y), extrude along -x

# Build on YZ workplane (since u=z, v=y)
wp = cq.Workplane("YZ")

# Outer rectangle in UV coordinates: u from -6.12 to -1.88, v from 10.88 to 15.12
# In YZ: u -> Z, v -> Y
outer_center_u = (-6.12 + -1.88) / 2  # = -4.0
outer_center_v = (10.88 + 15.12) / 2  # = 13.0
outer_width_u = abs(-1.88 - (-6.12))  # = 4.24
outer_height_v = abs(15.12 - 10.88)   # = 4.24

# Inner rectangle in UV coordinates: u from -6.0 to -2.0, v from 11.0 to 15.0
inner_center_u = (-6.0 + -2.0) / 2    # = -4.0
inner_center_v = (11.0 + 15.0) / 2    # = 13.0
inner_width_u = abs(-2.0 - (-6.0))    # = 4.0
inner_height_v = abs(15.0 - 11.0)     # = 4.0

# Build outer rectangle on YZ plane (u=Z, v=Y)
# Note: cadquery YZ plane: x=0, y=Y, z=Z
# So we map: u (Z) -> z, v (Y) -> y
outer = wp.moveTo(outer_center_v, outer_center_u).rect(outer_height_v, outer_width_u, centered=True)

# Build inner rectangle for cutting
inner = wp.moveTo(inner_center_v, inner_center_u).rect(inner_height_v, inner_width_u, centered=True)

# Extrude along -x direction (negative w_dir) by 1120.0 mm
# Since we're on YZ plane, extrude in -x direction
result = outer.extrude(-1120.0)

# Cut inner hole: extrude inner rectangle in same direction
cut_prism = inner.extrude(-1120.0)
result = result.cut(cut_prism)

# Ensure the result is a valid solid before export
if result.val().isValid():
    exporters.export(result, OUT_STEP_PATH)
else:
    # Fallback: try to fix by fusing and re-exporting
    result = result.fuse(result)
    exporters.export(result, OUT_STEP_PATH)
