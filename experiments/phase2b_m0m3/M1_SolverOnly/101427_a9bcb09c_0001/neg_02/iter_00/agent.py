import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0001\neg_02\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box) with one through void
# Outer rectangle: from (-2.5, -2.5) to (195.5, 57.5) in UV plane
# Inner rectangle: from (0, 0) to (193.0, 55.0) in UV plane
# Extrude 25.0 mm in +w direction (w = Y axis)
# Note: coordinates are in mm after cm->mm conversion (x10)

# Build outer rectangle
outer = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(198.0, 60.0, centered=True)

# Build inner rectangle for the void
inner = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(193.0, 55.0, centered=True)

# Extrude outer to create solid
solid = outer.extrude(25.0)

# Cut inner void
void = inner.extrude(25.0)
result = solid.cut(void)

exporters.export(result, OUT_STEP_PATH)
