import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40mm x 40mm (in UV plane)
# Inner rectangle: 37.6mm x 37.6mm (wall thickness 1.2mm)
# Extrude distance: 780mm along W direction (Y axis)
# Coordinate system: U=X, V=-Z, W=Y

# Build the outer rectangle profile
outer = cq.Workplane("XZ").moveTo(0, 0).rect(40, 40, centered=True)

# Build the inner rectangle profile (the hole)
inner = cq.Workplane("XZ").moveTo(0, 0).rect(37.6, 37.6, centered=True)

# Create the frame by extruding the outer rectangle and cutting the inner
# Extrude 780mm along Y (positive direction)
result = outer.extrude(780.0)

# Cut the inner hole - extrude the inner profile and subtract
inner_solid = inner.extrude(780.0)
result = result.cut(inner_solid)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0000\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
