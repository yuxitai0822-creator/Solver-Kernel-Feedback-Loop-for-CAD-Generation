import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0001\neg_02\iter_00/generated.step"

# Design Plan parameters (converted from cm to mm where needed)
# Outer rectangle: from UV coordinates (-2.5, 57.5) to (195.5, -2.5) in cm
# Converted to mm: multiply by 10
# Outer: x from -25 to 1955, y from -25 to 575
# Inner: x from 0 to 1930, y from 0 to 550
# Extrude distance: 25.0 mm

# Build the outer rectangle
outer = cq.Workplane("XZ").moveTo(965.0, 275.0).rect(1980.0, 600.0, centered=True)

# Build the inner rectangle (hole)
inner = cq.Workplane("XZ").moveTo(965.0, 275.0).rect(1930.0, 550.0, centered=True)

# Extrude the outer rectangle
result = outer.extrude(25.0)

# Cut the inner hole
cut_prism = inner.extrude(50.0)  # overshoot to ensure clean cut
result = result.cut(cut_prism)

exporters.export(result, OUT_STEP_PATH)
