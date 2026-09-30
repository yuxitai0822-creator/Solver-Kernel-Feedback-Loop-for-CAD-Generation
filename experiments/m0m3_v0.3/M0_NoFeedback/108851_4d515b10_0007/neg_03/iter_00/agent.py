import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
# The profile is a rectangle in the XZ plane (u=279.4 along X, v=50.8 along Z)
# Extrude along Y (w direction) by 19.05 mm

# Define dimensions from design plan
length_u = 279.4  # mm (along X)
width_v = 50.8    # mm (along Z)
extrude_w = 19.05 # mm (along Y)

# Build the part using CadQuery
# Workplane on XZ (Y normal) to match the frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The rectangle is centered at origin for simplicity, then extruded
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_w)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0007\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
