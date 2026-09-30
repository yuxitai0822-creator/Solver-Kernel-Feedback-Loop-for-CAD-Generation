import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from 0 to 27.94, v from 0 to 5.08
# Note: dimensions in design plan are in cm (27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm)
# Extrude along +w (y-axis) by 19.05 mm

# Build the rectangle profile in the XZ plane (since v_dir is -z, u_dir is x)
# The profile is a rectangle with corners at (0,0), (279.4,0), (279.4,50.8), (0,50.8)
# in the UV plane. Since u=x and v=-z, we map: u->x, v->-z
# So in XZ coordinates: x from 0 to 279.4, z from -50.8 to 0

result = (
    cq.Workplane("XZ")
    .center(279.4/2, -50.8/2)  # center of rectangle
    .rect(279.4, 50.8)
    .extrude(19.05)  # extrude along +y (w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0007\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)