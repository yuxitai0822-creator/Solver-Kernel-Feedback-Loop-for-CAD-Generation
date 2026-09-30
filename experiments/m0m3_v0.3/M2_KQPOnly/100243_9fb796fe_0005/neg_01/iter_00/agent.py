import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0005\neg_01\iter_00/generated.step"

# Design Plan: extruded rectangle (square strut)
# Profile: rectangle 19mm x 19mm (after cm->mm conversion: 1.9cm x 1.9cm = 19mm x 19mm)
# Extrude: 200mm (20.0cm -> 200mm) along +w direction
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The profile coordinates in UV space: center at (-57.27820137826746, -12.99014576968157)
# Width along U = 19.0, height along V = 19.0
# The UV coordinates given: u from -58.2782 to -56.3782 (width=1.9cm=19mm)
# v from -13.9401 to -12.0401 (height=1.9cm=19mm)

# Build on XY plane, then rotate to match frame orientation
# Frame: u=X, v=-Z, w=Y
# So we sketch on XZ plane (u=X, v=Z) but v_dir is -Z, so we need to negate Z
# Actually simpler: sketch on XY with rectangle, then rotate

# Create rectangle on XY plane centered at origin
# Width along X = 19.0, height along Y = 19.0
result = (cq.Workplane("XY")
    .rect(19.0, 19.0, centered=True)
    .extrude(200.0))

# Now rotate to match frame: u=X, v=-Z, w=Y
# The rectangle is currently in XY plane with normal +Z
# We need normal along +Y (w_dir), so rotate -90 deg around X axis
result = result.rotate((0,0,0), (1,0,0), -90)

# Now the part is oriented correctly: 
# - original X stays X (u_dir)
# - original Y becomes -Z (v_dir) after rotation
# - original Z becomes Y (w_dir)

# Translate to match the UV coordinate center
# The center in UV is at (-57.27820137826746, -12.99014576968157)
# After rotation: u -> X, v -> -Z
# So center in world: X = -57.27820137826746, Z = 12.99014576968157 (negated v), Y = 0
result = result.translate((-57.27820137826746, 0, 12.99014576968157))

exporters.export(result, OUT_STEP_PATH)
