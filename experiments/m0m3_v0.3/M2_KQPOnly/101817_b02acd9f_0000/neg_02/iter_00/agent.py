import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_02\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40x40 mm (in UV plane)
# Inner rectangle: 37.6x37.6 mm (wall thickness 1.2 mm)
# Extrude distance: 780 mm along W direction (Y axis)
# The UV plane is defined by U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# So sketch is on XZ plane, extrude along Y

# Build outer rectangle centered at origin
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(40, 40)
    .extrude(780)
)

# Build inner rectangle for the hole
inner = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(37.6, 37.6)
    .extrude(780)
)

# Subtract inner from outer to create hollow frame
result = result.cut(inner)

# Export
exporters.export(result, OUT_STEP_PATH)
