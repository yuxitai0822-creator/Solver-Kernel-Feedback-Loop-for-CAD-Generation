import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 500mm x 300mm
# Inner rectangle: 400mm x 200mm (centered, so offset 50mm from outer edges)
# Extrude distance: 500mm along +Z
# This creates a hollow box with one through void (the inner hole)

# Build the outer rectangle on XY plane
result = (cq.Workplane("XY")
          .rect(500, 300)  # outer rectangle centered at origin
          .extrude(500))   # extrude 500mm in +Z direction

# Cut the inner hole: create a rectangular prism and subtract
inner = (cq.Workplane("XY")
         .rect(400, 200)  # inner rectangle centered at origin
         .extrude(500))   # extrude same height

result = result.cut(inner)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0006\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)