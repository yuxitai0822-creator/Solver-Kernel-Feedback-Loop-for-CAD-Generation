import cadquery as cq
from cadquery import exporters
import math

# Design Plan: basic slat v1 (5)
# Extruded rectangle: 95.25 mm x 571.5 mm x 19.05 mm
# The profile is a rectangle in the UV plane, where:
#   U direction = (1,0,0) = X axis
#   V direction = (0,0,-1) = -Z axis
#   W direction = (0,1,0) = Y axis (extrude direction)
# Profile rectangle corners in UV:
#   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# But the dimensions say length_u = 95.25, width_v = 571.5
# The UV coordinates given are 9.525 and 57.15, which are 1/10 of the actual dimensions.
# This is because the original data was in cm and converted to mm (x10).
# So the actual rectangle in mm is: 95.25 mm x 571.5 mm
# The extrude distance is 19.05 mm along +W (Y axis)

# Build the part
result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5, centered=True)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101269_f084ba14_0023\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
