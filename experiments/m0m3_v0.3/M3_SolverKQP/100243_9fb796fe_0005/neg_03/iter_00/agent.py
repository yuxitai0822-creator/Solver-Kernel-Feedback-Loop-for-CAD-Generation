import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg Left - square strut
# Profile: rectangle 19mm x 19mm (in UV plane)
# Extrude: 200mm along +W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center at (-57.27820137826746, -13.0) in UV coordinates

# Build the rectangle profile on XZ plane (since V is -Z, U is X)
# The profile is centered at the midpoint of the given rectangle corners
# Corners in UV: (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
# Width in U: 1.9mm, Height in V: 1.9mm (but design says 19mm - scaling applied?)
# Actually the design plan says length_u=19.0, width_v=19.0
# The UV coordinates given are in mm after cm->mm conversion? Let's check:
# The coordinates are around -57 to -58 in U, -12 to -14 in V
# The span is 1.9mm in both directions - but design says 19mm
# This suggests the coordinates were scaled by 0.1 (cm to mm conversion factor 10)
# So actual dimensions: width=1.9*10=19mm, height=1.9*10=19mm
# We'll use the design plan dimensions directly: 19x19 rectangle

# Center of rectangle in UV: (-57.27820137826746, -13.0)
center_u = -57.27820137826746
center_v = -13.0
width_u = 19.0  # from design plan
height_v = 19.0  # from design plan

# Create workplane on XZ (since V is -Z, U is X)
# The frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# So sketch plane is XZ (U=X, V=-Z)
wp = cq.Workplane("XZ")

# Move to center and draw rectangle
# Note: in XZ plane, X corresponds to U, Z corresponds to -V
# So center in XZ: (center_u, -center_v) = (-57.2782, 13.0)
wp = wp.moveTo(center_u, -center_v)
wp = wp.rect(width_u, height_v, centered=True)

# Extrude along W direction (Y axis) by 200mm
result = wp.extrude(200.0)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0005\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)