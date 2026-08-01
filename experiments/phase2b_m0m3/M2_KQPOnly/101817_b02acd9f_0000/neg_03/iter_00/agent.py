import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (6.0, -7.0), (10.0, -7.0), (10.0, -3.0), (6.0, -3.0) in UV plane
# Inner rectangle (hole): corners at (6.12, -6.88), (6.12, -3.12), (9.88, -3.12), (9.88, -6.88)
# Extrude direction: +w (which maps to +Y in world), distance 780.0 mm
# The UV plane corresponds to XZ in world (u->X, v->Z, w->Y)

# Build outer rectangle on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(6.0, -7.0)
    .lineTo(10.0, -7.0)
    .lineTo(10.0, -3.0)
    .lineTo(6.0, -3.0)
    .close()
    .extrude(780.0)  # extrude in +Y direction
)

# Cut inner hole (the void)
inner = (
    cq.Workplane("XZ")
    .moveTo(6.12, -6.88)
    .lineTo(6.12, -3.12)
    .lineTo(9.88, -3.12)
    .lineTo(9.88, -6.88)
    .close()
    .extrude(780.0)  # same extrusion to cut through
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
