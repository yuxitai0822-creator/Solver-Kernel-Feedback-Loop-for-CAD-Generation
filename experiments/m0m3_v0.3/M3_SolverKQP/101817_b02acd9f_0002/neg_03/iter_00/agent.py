import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0002\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (-6.12, 10.88) to (-1.88, 15.12) in UV plane
# Inner rectangle: corners at (-6.0, 11.0) to (-2.0, 15.0) in UV plane
# Extrude along W direction (X axis) by 1120.0 mm
# The frame axes: U = -Z, V = +Y, W = +X
# So the profile is in the YZ plane (U=-Z, V=+Y)

# Build the outer rectangle
outer = cq.Workplane("YZ").moveTo(-4.0, 13.0).rect(4.24, 4.24, centered=True)

# Build the inner rectangle (hole)
inner = cq.Workplane("YZ").moveTo(-4.0, 13.0).rect(4.0, 4.0, centered=True)

# Create the profile by subtracting inner from outer
profile = outer.cut(inner)

# Extrude along X (W direction) by 1120.0 mm
result = profile.extrude(1120.0)

# Export
importers = cq.exporters
exporters.export(result, OUT_STEP_PATH)
