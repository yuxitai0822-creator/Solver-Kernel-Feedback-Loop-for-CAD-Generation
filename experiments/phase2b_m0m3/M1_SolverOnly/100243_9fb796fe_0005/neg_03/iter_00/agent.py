import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg Left - square strut
# Profile: rectangle 19.0mm x 19.0mm (in UV frame)
# Extrude: 200.0mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center in UV: (-57.27820137826746, -12.99014576968157)
# Profile half-widths: 9.5mm in U, 9.5mm in V

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0005\neg_03\iter_00\generated.step"

# Build the part using the frame axes from the design plan
# Workplane on XZ (since V is [0,0,-1] and W is [0,1,0], the sketch plane is XZ)
# The rectangle is defined in UV coordinates, where U=X, V=-Z
# Center of rectangle in UV: (-57.27820137826746, -12.99014576968157)
# Convert to XZ: x = u, z = -v
cx = -57.27820137826746
cz = 12.99014576968157  # -v since v = -z
w = 19.0
h = 19.0

# Create workplane on XZ
wp = cq.Workplane("XZ")

# Draw rectangle centered at (cx, cz) with dimensions w x h
result = wp.moveTo(cx, cz).rect(w, h, centered=True).extrude(200.0)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
