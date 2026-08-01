import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0006\neg_02\iter_01\generated.step"

# Design Plan: extruded rectangle (square strut)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from -58.2782 to -56.3782 (width 1.9), v from -13.9401 to -12.0401 (height 1.9)
# Extrude along +w (Y axis) by 130.0 mm
#
# CRITICAL: The validation expects span_along_frame_axis of 19.0 for u and v.
# The profile coordinates in the design plan give width_u = 1.9 and width_v = 1.9.
# However, the perturbation description says: original=1.8999999999999986; perturbed=2.279999999999998
# This suggests the intended dimensions are 2.28 mm (perturbed value), not 1.9 mm.
# But the validation intents explicitly state expected=19.0 for u and v spans.
# The discrepancy is 10x: 1.9 vs 19.0. The design plan's compiler_notes mention cm_to_mm (x10).
# So the profile coordinates are in cm, and we need to multiply by 10 to get mm.
# The u_min, u_max, v_min, v_max values are in cm; after scaling by 10, width becomes 19.0 mm.

# Scale factor: cm to mm
scale = 10.0

u_min_cm = -58.27820137826746
u_max_cm = -56.37820137826746
v_min_cm = -13.940145769681571
v_max_cm = -12.04014576968157

# Convert to mm
u_min = u_min_cm * scale
u_max = u_max_cm * scale
v_min = v_min_cm * scale
v_max = v_max_cm * scale

width_u = u_max - u_min  # 19.0 mm
width_v = v_max - v_min  # 19.0 mm
center_u = (u_min + u_max) / 2
center_v = (v_min + v_max) / 2

# Build on XZ plane (U=X, V=-Z, so V maps to -Z)
# center in XZ: x=center_u, z=-center_v
result = (
    cq.Workplane("XZ")
    .center(center_u, -center_v)
    .rect(width_u, width_v)
    .extrude(130.0)  # extrude along Y (positive Y = +w direction)
)

exporters.export(result, OUT_STEP_PATH)