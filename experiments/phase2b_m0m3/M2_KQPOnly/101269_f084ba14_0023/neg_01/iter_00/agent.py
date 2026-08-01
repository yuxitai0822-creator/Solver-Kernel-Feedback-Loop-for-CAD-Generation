import cadquery as cq
from cadquery import exporters
import math

# Design Plan: basic slat v1 (5)
# Extruded rectangle: 95.25 mm (u) x 571.5 mm (v) x 19.05 mm (w)
# The perturbation changes extrude depth from 1.905 cm to 2.8575 cm = 28.575 mm
# But the design plan specifies 19.05 mm. We follow the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101269_f084ba14_0023\neg_01\iter_00/generated.step"

# Build the rectangle profile on the XZ plane (as per previous script's WORKPLANE)
# The rectangle dimensions from design plan:
#   u (x direction): 95.25 mm
#   v (z direction): 571.5 mm (since v_dir = [0,0,-1])
# Extrude in w direction (y direction) by 19.05 mm

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Rectangle centered at origin, dimensions: width=95.25 (x), height=571.5 (z)
# The design plan's rectangle curves show:
#   start_uv: (9.525, 57.15) -> (9.525, 0.0)  (u from 0 to 9.525? Actually the values are in cm?)
# Wait, the design plan says unit_conversion_applied: cm_to_mm (x10)
# So the uv values in the design plan are in cm? Let's check:
#   curves: (9.525, 57.15) to (9.525, 0.0) etc.
#   length_u = 95.25 mm, width_v = 571.5 mm
# The rectangle spans from u=0 to u=95.25, v=0 to v=571.5
# So we create a rectangle from (0,0) to (95.25, 571.5) in uv space
# But the frame has u_dir = [1,0,0], v_dir = [0,0,-1]
# So u maps to x, v maps to -z
# The rectangle in xz plane: x from 0 to 95.25, z from -571.5 to 0

# Simpler: create a centered rectangle at (95.25/2, -571.5/2) with size (95.25, 571.5)
# But let's just use the exact coordinates from the design plan
# The curves define a rectangle from (0,0) to (95.25, 571.5) in uv
# In xz: x from 0 to 95.25, z from -571.5 to 0

# Build the rectangle using polyline
wp = wp.moveTo(0, 0)  # start at (x=0, z=0)
wp = wp.lineTo(95.25, 0)  # to (x=95.25, z=0)
wp = wp.lineTo(95.25, -571.5)  # to (x=95.25, z=-571.5)
wp = wp.lineTo(0, -571.5)  # to (x=0, z=-571.5)
wp = wp.close()  # back to (0,0)

# Extrude in +y direction (w direction) by 19.05 mm
result = wp.extrude(19.05)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
