import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle with dimensions:
#   length_u (X): 209.55 mm
#   width_v (Z): 57.912 mm
#   extrude_distance (Y): 19.05 mm
#
# Coordinate system:
#   u_dir = [1,0,0] (X)
#   v_dir = [0,0,-1] (Z, negative)
#   w_dir = [0,1,0] (Y)
#
# The rectangle is defined in UV space (XZ plane) and extruded along W (Y).
# The rectangle corners in UV:
#   (0, 0) -> (20.955, 0) -> (20.955, 5.7912) -> (0, 5.7912)
# But note: the design plan says length_u = 209.55, width_v = 57.912
# The UV coordinates given are 20.955 and 5.7912, which are 1/10 of the actual dimensions.
# This is because the original was in cm and converted to mm (x10).
# So we use the actual dimensions: 209.55 x 57.912 mm.

# Build the rectangle on the XZ plane (Y is extrusion direction)
result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912, centered=False)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0009\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
