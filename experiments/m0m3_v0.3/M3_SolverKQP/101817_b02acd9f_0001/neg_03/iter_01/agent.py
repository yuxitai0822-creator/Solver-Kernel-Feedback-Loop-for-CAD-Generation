import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0001\neg_03\iter_01/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40x40 mm (centered at origin)
# Inner rectangle: 37.6x37.6 mm (centered at origin)
# Extrude distance: 520 mm in +Z direction
# The perturbation description says 'void_remove' but the kernel feedback expects 1 through void.
# Therefore we must create a hollow box with one through void (the inner hole).

# Build outer rectangle
result = (cq.Workplane("XY")
          .rect(40.0, 40.0)
          .extrude(520.0)
          .faces(">Z")  # select top face
          .workplane()
          .rect(37.6, 37.6)  # inner rectangle
          .cutThruAll()  # cut through the entire body
          )

exporters.export(result, OUT_STEP_PATH)