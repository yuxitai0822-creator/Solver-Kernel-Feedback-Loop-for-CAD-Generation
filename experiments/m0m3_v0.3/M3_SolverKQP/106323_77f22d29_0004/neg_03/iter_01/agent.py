import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106323_77f22d29_0004\neg_03\iter_01/generated.step"

# Design Plan: extruded annulus
# Outer radius = 17.5 mm, Inner radius = 12.5 mm
# Extrude total distance = 10.0 mm, symmetric (both sides)
# Unit conversion: cm->mm already applied (x10)

# Build the annulus using a single Workplane with circle and hole
result = (cq.Workplane("XY")
          .circle(17.5)          # outer circle
          .circle(12.5)          # inner circle (hole)
          .extrude(5.0, both=True))  # symmetric extrusion, total 10.0 mm

# Export to STEP
exporters.export(result, OUT_STEP_PATH)