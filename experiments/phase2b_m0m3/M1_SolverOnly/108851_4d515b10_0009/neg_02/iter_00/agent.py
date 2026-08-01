import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle with dimensions:
#   length_u (x): 209.55 mm  (original 20.955 cm * 10)
#   width_v (z): 57.912 mm  (original 5.7912 cm * 10)
#   extrude_distance (y): 19.05 mm (original 1.905 cm * 10)
#
# Frame: u_dir = [1,0,0] (x), v_dir = [0,0,-1] (z), w_dir = [0,1,0] (y)
# Rectangle in uv-plane: u from 0 to 209.55, v from 0 to 57.912
# Extrude in +w direction (y) by 19.05 mm

# Build the rectangle on the XZ plane (since v_dir is -z, we use z for v)
# Workplane 'XZ' means sketch on xz plane, extrude in y direction
result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912, centered=False)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0009\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)