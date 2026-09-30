import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0001\neg_03\iter_00/generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion)
# Rectangle: length_u = 279.4 mm, width_v = 215.9 mm
# Extrude distance = 1.5875 mm
# The profile curves in the design plan show:
#   start_uv: (0.0, 21.59) -> (0.0, 0.0) -> (27.94, 0.0) -> (27.94, 21.59) -> (0.0, 21.59)
# But the dimensions table says length_u=279.4, width_v=215.9.
# The curves appear to be in cm (27.94 cm = 279.4 mm, 21.59 cm = 215.9 mm).
# So we build a rectangle of 279.4 x 215.9 mm, centered at origin.

# Build the base rectangle
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9, centered=True)
    .extrude(1.5875)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")