import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5 (in UV frame)
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# Extrude in +w direction by 25.0 mm
# UV frame: u = x, v = -z, w = y (per design plan frame axes)
# So we work on XZ plane, extrude in Y direction

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0001\neg_03\iter_00/generated.step"

# Build the outer rectangle on XZ plane
# Outer: u from -2.5 to 195.5, v from -2.5 to 57.5
# In XZ: x = u, z = -v (since v_dir = [0,0,-1])
# So outer: x from -2.5 to 195.5, z from -57.5 to 2.5
outer_xmin, outer_xmax = -2.5, 195.5
outer_zmin, outer_zmax = -57.5, 2.5
outer_w = outer_xmax - outer_xmin  # 198.0
outer_h = outer_zmax - outer_zmin  # 60.0
outer_cx = (outer_xmin + outer_xmax) / 2  # 96.5
outer_cz = (outer_zmin + outer_zmax) / 2  # -27.5

# Inner: u from 0.0 to 193.0, v from 0.0 to 55.0
# In XZ: x from 0.0 to 193.0, z from -55.0 to 0.0
inner_xmin, inner_xmax = 0.0, 193.0
inner_zmin, inner_zmax = -55.0, 0.0
inner_w = inner_xmax - inner_xmin  # 193.0
inner_h = inner_zmax - inner_zmin  # 55.0
inner_cx = (inner_xmin + inner_xmax) / 2  # 96.5
inner_cz = (inner_zmin + inner_zmax) / 2  # -27.5

# Build the frame
result = (
    cq.Workplane("XZ")
    .moveTo(outer_cx, outer_cz)
    .rect(outer_w, outer_h, centered=True)
    .extrude(25.0)  # extrude in +Y (which is +w direction)
)

# Cut inner hole
inner_cutter = (
    cq.Workplane("XZ")
    .moveTo(inner_cx, inner_cz)
    .rect(inner_w, inner_h, centered=True)
    .extrude(25.0 * 1.5)  # overshoot to ensure clean cut
)

result = result.cut(inner_cutter)

exporters.export(result, OUT_STEP_PATH)
