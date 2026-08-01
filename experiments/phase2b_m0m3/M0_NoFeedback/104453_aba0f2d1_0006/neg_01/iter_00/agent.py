import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangular frame
# Outer rectangle: 500mm x 300mm (u x v)
# Inner rectangle: 400mm x 200mm (u x v), offset 50mm from outer edges
# Extrude distance: 500mm along +w (z-axis)
# Unit conversion: all dimensions in mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0006\neg_01\iter_00\generated.step"

# Create the outer rectangle profile
result = (cq.Workplane("XY")
          .center(250, 150)  # center of 500x300 rectangle
          .rect(500, 300)
          .extrude(500))  # extrude 500mm in +Z

# Create the inner rectangle profile and cut it out
inner = (cq.Workplane("XY")
         .center(250, 150)  # same center
         .rect(400, 200)
         .extrude(500))  # extrude same height for clean cut

result = result.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
