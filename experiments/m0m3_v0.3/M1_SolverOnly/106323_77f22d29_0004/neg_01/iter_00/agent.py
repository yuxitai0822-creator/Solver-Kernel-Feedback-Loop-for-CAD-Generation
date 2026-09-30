import cadquery as cq
from cadquery import exporters
import math

# Design Plan: bearing 2 v1
# Extruded annulus: outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# Perturbation: OneSide extent (extrude in +Z direction only)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106323_77f22d29_0004\neg_01\iter_00\generated.step"

# Build the outer circle (radius 17.5 mm)
outer = cq.Workplane("XY").circle(17.5)

# Build the inner circle (radius 12.5 mm) for the hole
inner = cq.Workplane("XY").circle(12.5)

# Create the annulus by cutting inner from outer
annulus = outer.cut(inner)

# Extrude the annulus in +Z direction only (OneSide extent)
# Total distance is 10.0 mm (from z=0 to z=10.0)
result = annulus.extrude(10.0)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
