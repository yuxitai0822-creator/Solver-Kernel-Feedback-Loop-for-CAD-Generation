import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_03\iter_01/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (10.0, -7.0), (6.0, -7.0), (6.0, -3.0), (10.0, -3.0) in UV plane
#   -> u spans from 6.0 to 10.0 (length 4.0), v spans from -7.0 to -3.0 (length 4.0)
#   -> BUT expected outer dimensions are 40.0 x 40.0 mm (from design plan dimensions)
#   -> The UV coordinates were given in cm (unit_conversion_applied: cm_to_mm x10)
#   -> So multiply all UV coordinates by 10 to get mm
# Inner rectangle (hole): corners at (6.12, -6.88), (6.12, -3.12), (9.88, -3.12), (9.88, -6.88)
#   -> inner dimensions: u: 9.88-6.12=3.76 cm = 37.6 mm, v: -3.12-(-6.88)=3.76 cm = 37.6 mm
# Extrude direction: +w (which maps to +Y in world), distance 780.0 mm
# The UV plane corresponds to XZ in world (u->X, v->Z, w->Y)

# Scale factor: cm to mm
scale = 10.0

# Outer rectangle corners in cm, then scaled to mm
outer_cm = [(6.0, -7.0), (10.0, -7.0), (10.0, -3.0), (6.0, -3.0)]
outer_mm = [(x*scale, y*scale) for x, y in outer_cm]

# Inner rectangle corners in cm, then scaled to mm
inner_cm = [(6.12, -6.88), (6.12, -3.12), (9.88, -3.12), (9.88, -6.88)]
inner_mm = [(x*scale, y*scale) for x, y in inner_cm]

# Build outer rectangle on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(outer_mm[0][0], outer_mm[0][1])
    .lineTo(outer_mm[1][0], outer_mm[1][1])
    .lineTo(outer_mm[2][0], outer_mm[2][1])
    .lineTo(outer_mm[3][0], outer_mm[3][1])
    .close()
    .extrude(780.0)  # extrude in +Y direction
)

# Cut inner hole (the void)
inner = (
    cq.Workplane("XZ")
    .moveTo(inner_mm[0][0], inner_mm[0][1])
    .lineTo(inner_mm[1][0], inner_mm[1][1])
    .lineTo(inner_mm[2][0], inner_mm[2][1])
    .lineTo(inner_mm[3][0], inner_mm[3][1])
    .close()
    .extrude(780.0)  # same extrusion to cut through
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
