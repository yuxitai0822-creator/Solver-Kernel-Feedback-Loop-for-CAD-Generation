import cadquery as cq
from cadquery import exporters
import math

# Design Plan: bearing 2 v1
# Extruded annulus with outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# The perturbation changes extent from symmetric to one-side, so we extrude 10.0 mm in +Z direction

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106323_77f22d29_0004\neg_01\iter_00/generated.step"

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Build outer circle (radius 17.5 mm)
outer = wp.moveTo(0, 0).circle(17.5)

# Extrude 10.0 mm in +Z direction (one-side extent)
result = outer.extrude(10.0)

# Cut inner hole (radius 12.5 mm)
inner_wp = cq.Workplane("XY").moveTo(0, 0).circle(12.5)
inner_prism = inner_wp.extrude(10.0)
result = result.cut(inner_prism)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
