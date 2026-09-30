import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0004\neg_02\iter_00/generated.step"

# Design Plan: Tail Stock Lever - extruded disk
# Profile: circle with radius 11.938 mm (from dimensions.radius.value)
# Center UV: (8.077681, 8.284339) - this is the center in the sketch plane
# Extrude: 12.7 mm in +w direction (one side)

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Build the circle profile at the specified center
# The center_uv coordinates are in the sketch plane (XY)
center_x = 8.077681
center_y = 8.284339
radius = 11.938  # from dimensions.profiles[0].radius.value

# Create the circle and extrude
result = wp.moveTo(center_x, center_y).circle(radius).extrude(12.7)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
