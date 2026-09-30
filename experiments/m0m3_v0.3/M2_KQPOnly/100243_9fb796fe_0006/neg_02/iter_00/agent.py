import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0006\neg_02\iter_00\generated.step"

# Design Plan: extruded rectangle (square strut)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from -58.2782 to -56.3782 (width 1.9), v from -13.9401 to -12.0401 (height 1.9)
# Extrude along +w (Y axis) by 130.0 mm

# Build on XY plane, then rotate to match frame orientation
# The profile is defined in UV coordinates where U=X, V=-Z, W=Y
# So we sketch on XZ plane (U=X, V=-Z) and extrude along Y

# Rectangle center and dimensions in UV space
u_min = -58.27820137826746
u_max = -56.37820137826746
v_min = -13.940145769681571
v_max = -12.04014576968157

width_u = u_max - u_min  # 1.9 mm
width_v = v_max - v_min  # 1.9 mm
center_u = (u_min + u_max) / 2  # -57.32820137826746
center_v = (v_min + v_max) / 2  # -12.99014576968157

# Build on XZ plane (U=X, V=-Z, so V maps to -Z)
# center in XZ: x=center_u, z=-center_v
result = (
    cq.Workplane("XZ")
    .center(center_u, -center_v)
    .rect(width_u, width_v)
    .extrude(130.0)  # extrude along Y (positive Y = +w direction)
)

exporters.export(result, OUT_STEP_PATH)
