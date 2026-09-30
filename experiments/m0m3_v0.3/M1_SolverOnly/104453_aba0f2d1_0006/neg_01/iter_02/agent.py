import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangular frame
# Outer rectangle: 500mm x 300mm (u x v)
# Inner rectangle: 400mm x 200mm (u x v) - offset 50mm from edges
# Extrude distance: 500mm in +w direction

# Build the outer rectangle profile
outer = cq.Workplane("XY").rect(500, 300).extrude(500)

# Build the inner rectangle profile (to be subtracted)
inner = cq.Workplane("XY").rect(400, 200).extrude(500)

# Position inner rectangle centered within outer (50mm offset from each edge)
inner = inner.translate((50, 50, 0))

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0006\neg_01\iter_02\generated.step"
exporters.export(result, OUT_STEP_PATH)