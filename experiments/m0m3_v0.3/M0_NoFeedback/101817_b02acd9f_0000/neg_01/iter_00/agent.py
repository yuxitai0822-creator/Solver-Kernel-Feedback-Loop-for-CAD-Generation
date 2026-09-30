import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame
# Outer rectangle: 40x40 mm (centered at origin)
# Inner rectangle: 37.6x37.6 mm (centered at origin)
# Extrude distance: 780.0 mm along +Y
# Coordinate system: X right, Y up, Z out of plane

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0000\neg_01\iter_00\generated.step"

# Create workplane on XZ plane (Y is extrusion direction)
wp = cq.Workplane("XZ")

# Outer rectangle: 40x40 mm centered at origin
outer = wp.center(0, 0).rect(40, 40).extrude(780.0)

# Inner rectangle: 37.6x37.6 mm centered at origin, extruded through
inner = cq.Workplane("XZ").center(0, 0).rect(37.6, 37.6).extrude(780.0)

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
