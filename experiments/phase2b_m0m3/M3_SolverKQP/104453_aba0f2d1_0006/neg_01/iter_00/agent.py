import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0006\neg_01\iter_00/generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion):
# Outer rectangle: 500 x 300 mm
# Inner rectangle: 400 x 200 mm (5 mm offset from outer edges)
# Extrude distance: 500 mm (one side, +Z direction)

# Build the outer rectangle profile
outer = cq.Workplane("XY").rect(500, 300, centered=False).extrude(500)

# Build the inner rectangle profile (the hole)
inner = cq.Workplane("XY").rect(400, 200, centered=False).extrude(500)

# Position inner rectangle: offset by (50, 50) from origin to match design plan
# Outer starts at (0,0) and goes to (500,300)
# Inner starts at (50,50) and goes to (450,250)
inner = inner.translate((50, 50, 0))

# Cut the inner hole from the outer body
result = outer.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
