import cadquery as cq
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_02\iter_02/generated.step"

# Build stadium profile using CadQuery primitives
# Stadium: straight length 500mm, radius 50mm, extrude 100mm

# Create workplane
wp = cq.Workplane("XY")

# Build the stadium shape by combining two circles and a rectangle
# Left circle at (0,0) radius 50
left_circle = wp.moveTo(0, 0).circle(50)

# Right circle at (500,0) radius 50
right_circle = wp.moveTo(500, 0).circle(50)

# Rectangle connecting them: width 500, height 100, centered at (250, 0)
rect = wp.moveTo(250, 0).rect(500, 100, centered=True)

# Union the shapes to form the stadium profile
stadium_profile = left_circle.union(right_circle).union(rect)

# Extrude the profile by 100mm in the +Z direction
result = stadium_profile.extrude(100.0)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
