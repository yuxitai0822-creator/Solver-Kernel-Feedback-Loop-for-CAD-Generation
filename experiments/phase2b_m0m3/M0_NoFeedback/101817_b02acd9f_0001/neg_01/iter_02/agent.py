import cadquery as cq
from cadquery import exporters

# Design Plan: horizontal leg 1
# Extruded rectangular frame with outer 40x40 mm and inner 37.6x37.6 mm
# Extrude distance: 520.0 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0001\neg_01\iter_02\generated.step"

# Create the outer rectangle as a solid box
result = (cq.Workplane("XY")
          .rect(40, 40)
          .extrude(520.0))

# Cut the inner rectangle hole
result = (result
          .faces("<Z")
          .workplane()
          .rect(37.6, 37.6)
          .cutThruAll())

# Export using correct function name
exporters.export(result, OUT_STEP_PATH)
