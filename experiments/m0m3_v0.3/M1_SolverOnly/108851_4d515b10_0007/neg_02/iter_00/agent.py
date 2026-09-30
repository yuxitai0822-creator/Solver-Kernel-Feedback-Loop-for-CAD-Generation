import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Profile rectangle in UV plane: u from 0 to 27.94, v from 0 to 5.08
# Note: Design plan dimensions are in mm, but the profile coordinates are in cm (27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm)
# The extrude direction is +w (along y-axis) for 19.05 mm

# Build the rectangle profile in the UV plane (XZ plane in CadQuery)
# u -> X axis, v -> Z axis (since v_dir = [0,0,-1], we use positive Z for simplicity)
# w -> Y axis (extrude direction)

# Rectangle corners in UV (cm): (0,0), (27.94,0), (27.94,5.08), (0,5.08)
# Convert to mm: (0,0), (279.4,0), (279.4,50.8), (0,50.8)

# Create workplane on XZ plane (Y is normal)
result = (cq.Workplane("XZ")
    .center(279.4/2, 50.8/2)  # center the rectangle
    .rect(279.4, 50.8)
    .extrude(19.05)  # extrude along Y (positive w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0007\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)