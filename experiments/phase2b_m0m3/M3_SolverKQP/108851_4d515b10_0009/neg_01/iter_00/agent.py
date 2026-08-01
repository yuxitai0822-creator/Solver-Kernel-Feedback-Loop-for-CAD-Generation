import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle: 209.55 x 57.912 mm, extrude 19.05 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means sketch is on XZ plane, extrude along Y (w_dir)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0009\neg_01\iter_00/generated.step"

# Rectangle dimensions from design plan
length_u = 209.55  # along u_dir = X axis
width_v = 57.912   # along v_dir = Z axis (negative direction)
extrude_w = 19.05  # along w_dir = Y axis

# Build the part
# Workplane on XZ (since v_dir is [0,0,-1], normal is Y)
result = (cq.Workplane("XZ")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_w))

# Export
exporters.export(result, OUT_STEP_PATH)
