import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106323_77f22d29_0004\neg_03\iter_00/generated.step"

# Design Plan: extruded annulus
# Outer radius = 17.5 mm, Inner radius = 12.5 mm
# Extrude total distance = 10.0 mm, symmetric (both sides)
# Unit conversion: cm->mm already applied (x10)

# Build the outer circle
outer_circle = cq.Workplane("XY").circle(17.5)

# Build the inner circle for the hole
inner_circle = cq.Workplane("XY").circle(12.5)

# Create the annulus by cutting inner from outer
annulus = outer_circle.cut(inner_circle)

# Extrude symmetrically: total 10.0 mm means 5.0 mm each side
result = annulus.extrude(5.0, both=True)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
