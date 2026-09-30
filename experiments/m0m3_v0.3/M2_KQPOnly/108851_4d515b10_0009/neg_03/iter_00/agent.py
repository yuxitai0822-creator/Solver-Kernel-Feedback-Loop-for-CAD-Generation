import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle with dimensions:
#   length_u (X): 209.55 mm
#   width_v (Z): 57.912 mm  (note: v_dir = [0,0,-1], so width is along Z)
#   extrude_distance (Y): 19.05 mm (along w_dir = [0,1,0])
#
# The profile rectangle in UV coordinates:
#   u: 0 to 20.955 (but note: length_u = 209.55, so scaling factor = 10?)
#   v: 0 to 5.7912 (but width_v = 57.912, scaling factor = 10)
# Actually the UV values are in cm (original design in cm, converted to mm by x10).
# So rectangle in mm: u: 0 to 209.55, v: 0 to 57.912
#
# Frame: u_dir = [1,0,0] (X), v_dir = [0,0,-1] (negative Z), w_dir = [0,1,0] (Y)
# So sketch plane is XZ (u along X, v along -Z), extrude along Y.

# Build the rectangle on XZ plane
result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912, centered=False)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0009\neg_03\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)