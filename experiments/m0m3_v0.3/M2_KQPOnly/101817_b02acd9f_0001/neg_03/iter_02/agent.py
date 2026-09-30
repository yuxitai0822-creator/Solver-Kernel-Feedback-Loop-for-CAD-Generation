import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0001\neg_03\iter_02/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40x40 mm (centered at origin)
# Inner rectangle: 37.6x37.6 mm (centered at origin)
# Extrude distance: 520 mm in +Z direction

# Build the outer box first
result = (cq.Workplane("XY")
          .rect(40.0, 40.0, centered=True)
          .extrude(520.0)
          .faces(">Z")  # select top face
          .workplane()
          .rect(37.6, 37.6, centered=True)
          .cutThruAll()  # cut through the entire solid
         )

# Export the result
exporters.export(result, OUT_STEP_PATH)