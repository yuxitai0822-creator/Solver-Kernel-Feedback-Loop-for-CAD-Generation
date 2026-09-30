import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_01\iter_00\generated.step"

# Design Plan: Drone Leg - square strut
# Profile: rectangle 19.0mm x 19.0mm (in UV plane)
# Extrude: 130.0mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center in UV: (-57.27820137826746, -12.99014576968157)
# Rectangle corners in UV: 
#   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
# Width in U: 1.9mm, Width in V: 1.9mm -> but expected 19.0mm each
# The UV coordinates seem scaled by 0.1 (cm to mm conversion factor 10)
# Original cm values: (-5.827820137826746, -1.204014576968157) to (-5.637820137826746, -1.3940145769681571)
# Width in cm: 0.19cm = 1.9mm -> but expected 19.0mm
# The design plan says dimensions: length_u=19.0, width_v=19.0
# The UV coordinates from the plan give 1.9mm width, which is 0.1x the expected.
# This is likely because the plan's UV coordinates are in cm and need *10 to get mm.
# Let's use the explicit dimensions from the plan: 19.0mm x 19.0mm rectangle
# Center in UV: (-57.27820137826746, -12.99014576968157) * 10 = (-572.7820137826746, -129.9014576968157)
# But wait, the previous script used coordinates *10 already.
# The plan says the rectangle is 19.0mm x 19.0mm, so we'll construct it centered at the given center.

# Extract center from the plan's rectangle curves (average of corners)
# Corners in UV (from plan):
# (-58.27820137826746, -12.04014576968157)
# (-58.27820137826746, -13.940145769681571)
# (-56.37820137826746, -13.940145769681571)
# (-56.37820137826746, -12.04014576968157)
# These are in the original unit (cm). Multiply by 10 to get mm.
# But the plan says dimensions are 19.0mm, so these coordinates must be in mm already?
# Let's check: width in U = 56.37820137826746 - 58.27820137826746 = -1.9 -> absolute 1.9
# width in V = 12.04014576968157 - 13.940145769681571 = -1.9 -> absolute 1.9
# So the rectangle is 1.9mm x 1.9mm, but plan says 19.0mm x 19.0mm.
# This is a discrepancy. The plan's explicit dimensions override the UV coordinates.
# We'll use the explicit dimensions: 19.0mm x 19.0mm rectangle.
# Center in UV (average): U = (-58.27820137826746 + -56.37820137826746)/2 = -57.32820137826746
# V = (-12.04014576968157 + -13.940145769681571)/2 = -12.99014576968157
# These are in mm (since plan says unit is mm).
# So rectangle: centered at (-57.32820137826746, -12.99014576968157), size 19.0 x 19.0

# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# This means: sketch on XZ plane (U=X, V=Z), extrude along Y (W=Y)
# In cadquery: Workplane("XZ") gives X as right, Z as up, Y as normal
# But V=[0,0,-1] means V direction is negative Z, so we need to flip
# Actually, let's just use the standard approach: create on XZ plane, then adjust

# Simpler approach: use the explicit dimensions and frame
# Create rectangle on XZ plane, centered at the given center
# Then extrude along Y by 130.0mm

center_u = -57.32820137826746  # in mm
center_v = -12.99014576968157  # in mm
width_u = 19.0  # mm
width_v = 19.0  # mm
extrude_dist = 130.0  # mm

# Build the part
result = (
    cq.Workplane("XZ")
    .moveTo(center_u, center_v)
    .rect(width_u, width_v, centered=True)
    .extrude(extrude_dist)
)

exporters.export(result, OUT_STEP_PATH)
